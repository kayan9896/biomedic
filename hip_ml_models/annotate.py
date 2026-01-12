"""
Lightweight inference wrapper for landmark regression models trained with
`annotation.py` (LandmarkRegressor).

Provides:
 - `AnnotationModel` class to load a saved checkpoint (uses checkpoint `meta` if present)
 - `predict(image_path)` to get normalized and pixel coordinates for centers and vectors
 - `visualize(image_path, ...)` to overlay predicted centers and anchored vectors on the image
 - `predict(image)` to get normalized and pixel coordinates for centers and vectors
 - `visualize(image_path, ...)` to overlay predicted centers and anchored vectors on the image

 
Supports:
- Multiple axis representations
- Metadata-driven decoding
- Visualization of axes according to their representations

This module intentionally keeps functionality minimal (no batch processing or saving
landmarks) — just single-image predict + visualize as requested.
"""
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import warnings

import cv2
import numpy as np
import torch
import torch.nn as nn
from torchvision.models import resnet18

try:
    from PIL import Image
except Exception:
    Image = None

try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None


# -----------------------------
# Axis representations (INFERENCE ONLY)
# -----------------------------

class AxisRepresentation:
    name: str
    dim: int

    def decode(self, pred: torch.Tensor, image_size):
        raise NotImplementedError


class AxisAnchorDir(AxisRepresentation):
    name = "anchor_dir"
    dim = 2

    def decode(self, pred, image_size):
        v = pred / (torch.norm(pred, dim=-1, keepdim=True) + 1e-8)
        return {"direction": v}


class AxisRhoTheta(AxisRepresentation):
    name = "rho_theta"
    dim = 2

    def decode(self, pred, image_size):
        W, H = image_size
        diag = (W * W + H * H) ** 0.5

        rho = pred[..., 0] * diag
        theta = pred[..., 1]

        n = torch.stack([torch.cos(theta), torch.sin(theta)], dim=-1)
        d = torch.stack([-n[..., 1], n[..., 0]], dim=-1)

        cx, cy = W / 2, H / 2
        p0 = rho[..., None] * n
        p0[..., 0] += cx
        p0[..., 1] += cy

        return {
            "normal": n,
            "direction": d,
            "point": p0,
            "rho": rho,
        }

class AxisRhoDir(AxisRepresentation):
    name = "rho_dir"
    dim = 3

    def decode(self, pred, image_size):
        """
        pred: (..., 3) -> (rho, dx, dy)
        """
        W, H = image_size
        diag = (W * W + H * H) ** 0.5

        rho = pred[..., 0] * diag
        d = pred[..., 1:3]
        d = d / (torch.norm(d, dim=-1, keepdim=True) + 1e-8)

        # normal is perpendicular to direction
        n = torch.stack([-d[..., 1], d[..., 0]], dim=-1)

        cx, cy = W / 2, H / 2
        p0 = rho[..., None] * n
        p0[..., 0] += cx
        p0[..., 1] += cy

        return {
            "rho": rho,
            "direction": d,
            "normal": n,
            "point": p0,
        }


AXIS_REPR_REGISTRY = {
    "anchor_dir": AxisAnchorDir,
    "rho_theta": AxisRhoTheta,
    "rho_dir": AxisRhoDir,
}

# -----------------------------
# Visualization utilities
# -----------------------------

def _clip_line_to_image(point, direction, w, h):
    """
    Exact clipping of an infinite line to image bounds using Liang–Barsky.
    Preserves true line position and orientation.
    """
    x0, y0 = point
    dx, dy = direction

    eps = 1e-9

    p = np.array([-dx, dx, -dy, dy])
    q = np.array([x0, w - x0, y0, h - y0])

    t0, t1 = -np.inf, np.inf

    for pi, qi in zip(p, q):
        if abs(pi) < eps:
            if qi < 0:
                return None
        else:
            t = qi / pi
            if pi < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)

    if t0 > t1:
        return (w/2, h/2), (w/2, h/2)

    p1 = (x0 + t0 * dx, y0 + t0 * dy)
    p2 = (x0 + t1 * dx, y0 + t1 * dy)

    return p1, p2

def _line_endpoints_from_anchor(anchor_xy, vec_xy, w, h, length=0.2):
    """
    Anchor is normalized coords [0..1], vec is unit vector.
    length: fraction of image width/height for displayed arrow (fraction of min dimension)
    """
    ax = anchor_xy[0] * w
    ay = anchor_xy[1] * h
    # use fraction of min(w,h)
    Lpx = length * min(w, h)
    ex = ax + vec_xy[0] * Lpx
    ey = ay + vec_xy[1] * Lpx
    return (ax, ay), (ex, ey)

# -----------------------------
# Model
# -----------------------------

class ChannelAttention(nn.Module):
    """Squeeze-and-Excitation style attention block."""
    def __init__(self, in_channels: int, reduction: int = 8):
        super().__init__()
        self.fc = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(in_channels, in_channels // reduction, kernel_size=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels // reduction, in_channels, kernel_size=1),
            nn.Sigmoid()
        )
    def forward(self, x):
        return x * self.fc(x)

class LandmarkRegressor(nn.Module):
    """
    ResNet18-based regressor:
      - flexible in_channels (1 or 1+M)
      - predicts n_centers*2 + n_axes*axis_dim outputs
    """
    def __init__(self, in_channels=1, n_centers=0, n_axes=0, axis_dim=2, pretrained=True, dropout=0.3):
        super().__init__()
        self.n_centers = n_centers
        self.n_axes = n_axes
        self.axis_dim = axis_dim

        res = resnet18(weights='IMAGENET1K_V1' if pretrained else None)
        old_conv = res.conv1
        # Replace conv1 to accept in_channels
        res.conv1 = nn.Conv2d(in_channels, old_conv.out_channels,
                              kernel_size=old_conv.kernel_size, stride=old_conv.stride,
                              padding=old_conv.padding, bias=False)
        if pretrained and in_channels == 1:
            # average RGB weights to initialize the single-channel conv
            with torch.no_grad():
                res.conv1.weight = nn.Parameter(old_conv.weight.mean(dim=1, keepdim=True))
        # if in_channels > 1 and pretrained, first conv will be randomly initialized (training adapts)
        self.backbone = nn.Sequential(*list(res.children())[:-2])  # remove avgpool & fc

        self.att = ChannelAttention(512)
        self.pool1 = nn.AdaptiveAvgPool2d(1)
        self.pool2 = nn.AdaptiveAvgPool2d(2)
        self.flatten_dim = 512 * (1*1 + 2*2)  # 512*(1 + 4) = 2560
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Sequential(
            nn.Linear(self.flatten_dim, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(256, (self.n_centers * 2) + (self.n_axes * self.axis_dim))
        )

    def forward(self, x):
        feat = self.backbone(x)  # [B, 512, H/32, W/32]
        feat = self.att(feat)
        pooled = torch.cat([self.pool1(feat).flatten(1), self.pool2(feat).flatten(1)], dim=1)
        out = self.fc(self.dropout(pooled))
        # split centers and vectors explicitly
        if self.n_centers > 0:
            # centers = torch.sigmoid(out[:, :self.n_centers*2])  # normalized [0..1]
            centers = out[:, :self.n_centers*2]   # unrestricted regression to allow points outside the image
        else:
            centers = out.new_zeros((out.size(0), 0))
        if self.n_axes > 0:
            vecs = out[:, self.n_centers*2:]
            vecs = vecs.view(-1, self.n_axes, self.axis_dim)
            vecs = vecs.view(-1, self.n_axes * self.axis_dim)
        else:
            vecs = out.new_zeros((out.size(0), 0))
        return torch.cat([centers, vecs], dim=1)

class AnnotationModel:
    """Inference helper for LandmarkRegressor models saved from `annotation.py`.

    Loads checkpoint and its `meta` (if present) to configure the model. Supports
    single-image inference (grayscale), assuming the model was trained with the
    image channel configuration saved in `meta['in_channels']`.
    """

    def __init__(self, model_path: str, device: Optional[str] = None):
        self.model_path = Path(model_path)
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device)

        self.model: Optional[torch.nn.Module] = None
        self.meta: Dict[str, Any] = {}
        self._load_model()

    def _load_model(self) -> None:
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        ck = torch.load(str(self.model_path), map_location=self.device)

        # Support common checkpoint shapes: {'state_dict'|'model_state_dict', 'meta'}
        if isinstance(ck, dict):
            # pull meta if present
            self.meta = ck.get("meta", {}) or {}
            # try several common state-dict keys
            if "state_dict" in ck:
                state_dict = ck["state_dict"]
            elif "model_state_dict" in ck:
                state_dict = ck["model_state_dict"]
            elif "model_state" in ck:
                state_dict = ck["model_state"]
            else:
                # assume ck itself is a state_dict
                state_dict = ck
        else:
            # raw state dict
            state_dict = ck
            self.meta = {}

        # fallbacks for meta fields
        in_ch = int(self.meta.get("in_channels", self.meta.get("in_channels", 1)))
        n_centers = int(self.meta.get("n_centers", 0))
        n_axes = int(self.meta.get("n_axes", 0))
        image_size = tuple(self.meta.get("image_size", (256, 256)))

        # get axis representation
        axis_repr_str = self.meta.get("axis_repr", "anchor_dir")
        self.axis_repr = AXIS_REPR_REGISTRY.get(axis_repr_str, AxisAnchorDir)()
        self.axis_dim = self.axis_repr.dim

        # instantiate model (don't attempt to load pretrained weights here)
        model = LandmarkRegressor(in_channels=in_ch, n_centers=n_centers, n_axes=n_axes, axis_dim=self.axis_dim, pretrained=False)
        model = model.to(self.device)

        # load state dict (handle DataParallel 'module.' prefix)
        try:
            model.load_state_dict(state_dict)
        except Exception:
            # strip possible 'module.' prefixes
            new_sd = {}
            for k, v in state_dict.items():
                nk = k.replace("module.", "") if k.startswith("module.") else k
                new_sd[nk] = v
            model.load_state_dict(new_sd)

        model.eval()
        self.model = model

        # ensure meta has useful defaults
        self.meta.setdefault("in_channels", in_ch)
        self.meta.setdefault("n_centers", n_centers)
        self.meta.setdefault("n_axes", n_axes)
        self.meta.setdefault("image_size", image_size)
        # landmarks list and axes may be present for visualization
        self.meta.setdefault("landmarks", self.meta.get("landmarks", []))
        self.meta.setdefault("axes", self.meta.get("axes", []))

        print(f"Annotation model loaded from ({self.model_path}) to ({self.device}): {in_ch} input channels, {n_centers} points, {n_axes} axes ({axis_repr_str}).")

    def predict(self, image: Any, return_pixels: bool = True, length: float = 0.2, readable_keys: bool = False) -> Dict[str, Any]:
        """Predict landmark points and anchored vectors for a single image.

        Args:
            image: path or image-like object (str/Path, PIL.Image, numpy.ndarray, or torch.Tensor)
            return_pixels: if True, returned coordinates are in pixel space, otherwise normalized
            length: length of vectors. Interpreted as fraction of min(image_dim) when
                `return_pixels` is True (converted to pixels), or as fraction in normalized
                coordinates when `return_pixels` is False. Default: 0.2

        Returns:
            dict with keys:
             - 'points': {landmark_name: (x, y), ...}
             - 'vectors': {(A_name, B_name): ((ax, ay), (bx, by)), ...}

        This replaces the older predict which returned raw arrays; points are labeled
        using `self.meta['landmarks']` and axes from `self.meta['axes']`.
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")

        # Support several input types: file path (str/Path), PIL Image, numpy array, or torch tensor.
        # Convert to a single-channel grayscale numpy array (uint8) named `img` with shape (H, W).
        img = None
        p = None
        # 1) Path / str: read via OpenCV (grayscale) with PIL fallback
        if isinstance(image, (str, Path)):
            p = Path(image)
            if not p.exists():
                raise FileNotFoundError(f"Image not found: {image}")
            img = cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)
            if img is None:
                # fallback to PIL
                if Image is not None:
                    pil = Image.open(str(p)).convert("L")
                    img = np.asarray(pil)
                else:
                    raise ValueError(f"Failed to read image: {image}")

        # 2) PIL Image
        elif Image is not None and isinstance(image, Image.Image):
            pil = image.convert("L")
            img = np.asarray(pil)

        # 3) Torch tensor
        elif isinstance(image, torch.Tensor):
            t = image.detach().cpu()
            # handle (C,H,W) or (H,W) or (H,W,C)
            if t.ndim == 3 and t.shape[0] in (1, 3, 4):
                t = t.permute(1, 2, 0)
            arr_np = t.numpy()
            # if float in [0,1], scale
            if np.issubdtype(arr_np.dtype, np.floating):
                arr_np = np.clip(arr_np, 0.0, 1.0)
                arr_np = (arr_np * 255.0).astype(np.uint8)
            else:
                arr_np = arr_np.astype(np.uint8)
            # now treat as numpy path below
            image = arr_np

        # 4) numpy array
        if img is None and isinstance(image, np.ndarray):
            arr = image
            # if channels-first (C,H,W), convert to H,W,C
            if arr.ndim == 3 and arr.shape[0] in (1, 3, 4) and arr.shape[0] < arr.shape[1]:
                arr = np.transpose(arr, (1, 2, 0))

            # float -> uint8
            if np.issubdtype(arr.dtype, np.floating):
                arr = np.clip(arr, 0.0, 1.0)
                arr = (arr * 255.0).astype(np.uint8)
            else:
                arr = arr.astype(np.uint8)

            # if multi-channel, convert RGB(A) -> grayscale
            if arr.ndim == 3 and arr.shape[2] in (3, 4):
                try:
                    img = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
                except Exception:
                    # final fallback: average channels
                    img = arr[..., :3].mean(axis=2).astype(np.uint8)
            elif arr.ndim == 2:
                img = arr
            else:
                raise ValueError("Unsupported numpy image shape: {}".format(arr.shape))

        if img is None:
            raise TypeError("Unsupported input type for `predict`. Accepts file path (str/Path), PIL.Image, numpy.ndarray, or torch.Tensor.")

        orig_h, orig_w = img.shape[:2]
        target_w, target_h = tuple(self.meta.get("image_size", (256, 256)))

        # resize to model input size (training used this convention)
        if (orig_w, orig_h) != (target_w, target_h):
            img_resized = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_AREA)
        else:
            img_resized = img

        arr = img_resized.astype(np.float32) / 255.0

        in_ch = int(self.meta.get("in_channels", 1))
        if in_ch != 1:
            raise NotImplementedError(f"Model expects in_channels={in_ch}. This wrapper only supports single-channel image input.")

        tensor = torch.from_numpy(arr)[None, None, :, :].float().to(self.device)

        with torch.no_grad():
            out = self.model(tensor)

        out = out.cpu().numpy().ravel()

        n_centers = int(self.meta.get("n_centers", 0))
        n_axes = int(self.meta.get("n_axes", 0))

        centers_norm = out[: n_centers * 2].reshape(-1, 2) if n_centers > 0 else np.zeros((0, 2), dtype=np.float32)
        vecs_pred = out[n_centers * 2 :].reshape(n_axes, self.axis_dim) if n_axes > 0 else np.zeros((0, self.axis_dim), dtype=np.float32)

        # compute pixel-space centers if requested
        centers_px = None
        if return_pixels:
            sx = float(orig_w) / float(target_w)
            sy = float(orig_h) / float(target_h)
            centers_px = np.empty_like(centers_norm)
            if centers_norm.shape[0] > 0:
                centers_px[:, 0] = centers_norm[:, 0] * target_w * sx
                centers_px[:, 1] = centers_norm[:, 1] * target_h * sy
            else:
                centers_px = centers_norm.copy()

        # build labeled points dict
        landmarks = list(self.meta.get("landmarks", []))
        axes = list(self.meta.get("axes", []))

        # helper to create readable labels if requested
        def _format_label(s: str) -> str:
            if not isinstance(s, str):
                return s
            s = s.strip("_")
            s = s.replace("_", " ")
            return s.title()

        # keep original-name mapping for internal lookups, then optionally produce a readable-key mapping
        points_orig: Dict[str, tuple] = {}
        if return_pixels:
            for i, name in enumerate(landmarks):
                if i < centers_px.shape[0]:
                    points_orig[name] = (float(centers_px[i, 0]), float(centers_px[i, 1]))
        else:
            for i, name in enumerate(landmarks):
                if i < centers_norm.shape[0]:
                    points_orig[name] = (float(centers_norm[i, 0]), float(centers_norm[i, 1]))

        # final points mapping returned to user (may have readable keys)
        points: Dict[str, tuple] = {}
        if readable_keys:
            for orig_name, coord in points_orig.items():
                points[_format_label(orig_name)] = coord
        else:
            points = dict(points_orig)

        # determine vector length in appropriate units
        vectors: Dict[tuple, tuple] = {}
        if return_pixels:
            # prefer original image size for pixel length
            min_dim = float(min(orig_w, orig_h)) if (orig_w and orig_h) else 1.0
            Lpx = float(length) * min_dim

        for i in range(n_axes):
            if i >= len(axes):
                continue
            A_name, B_name = axes[i]

            # decode the prediction to get direction
            pred_tensor = torch.from_numpy(vecs_pred[i]).float()
            decoded = self.axis_repr.decode(pred_tensor, self.meta["image_size"])
            direction = decoded["direction"].cpu().numpy()
            vx, vy = direction

            # determine anchor point
            if "point" in decoded:
                # For representations like rho_theta that define global lines, use the decoded point as anchor
                point_px = decoded["point"].cpu().numpy()
                if return_pixels:
                    sx = float(orig_w) / float(target_w)
                    sy = float(orig_h) / float(target_h)
                    anchor = (float(point_px[0] * sx), float(point_px[1] * sy))
                else:
                    # normalized coordinates
                    anchor = (float(point_px[0] / target_w), float(point_px[1] / target_h))
            else:
                # For anchor-based representations, use landmark A
                anchor = points_orig.get(A_name)
                anchor_idx = None
                if anchor is None:
                    for j, nm in enumerate(landmarks):
                        if A_name.lower() in nm.lower() or nm.lower() in A_name.lower():
                            anchor_idx = j
                            break
                    if anchor_idx is None:
                        continue
                    if return_pixels:
                        anchor = (float(centers_px[anchor_idx, 0]), float(centers_px[anchor_idx, 1]))
                    else:
                        anchor = (float(centers_norm[anchor_idx, 0]), float(centers_norm[anchor_idx, 1]))

            if return_pixels:
                bx = anchor[0] + vx * Lpx
                by = anchor[1] + vy * Lpx
            else:
                bx = anchor[0] + vx * float(length)
                by = anchor[1] + vy * float(length)

            # choose key style for returned vectors
            if readable_keys:
                key = (_format_label(A_name), _format_label(B_name))
            else:
                key = (A_name, B_name)

            vectors[key] = (anchor, (bx, by))

        return {"points": points, "vectors": vectors}

    def visualize(
        self,
        image_path: str,
        pred: Optional[Dict[str, Any]] = None,
        show: bool = True,
        save_path: Optional[str] = None,
        point_color: Tuple[int, int, int] = (0, 255, 0),
        vector_color: Tuple[int, int, int] = (0, 255, 0),
        length_fraction: float = 0.2,
    ) -> np.ndarray:
        """Overlay predicted centers and anchored vectors on the original image.

        If `pred` is omitted, `predict()` is run. `length_fraction` controls arrow length
        as fraction of min(image_dim).
        Returns the BGR image with overlays.
        """
        p = Path(image_path)
        if not p.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        if pred is None:
            pred = self.predict(image_path, return_pixels=True, length=length_fraction)

        img_color = cv2.imread(str(p), cv2.IMREAD_COLOR)
        if img_color is None:
            # fallback to PIL if OpenCV couldn't read color
            if Image is not None:
                pil = Image.open(str(p)).convert("RGB")
                img_color = cv2.cvtColor(np.asarray(pil), cv2.COLOR_RGB2BGR)
            else:
                raise ValueError(f"Failed to load image for visualization: {image_path}")

        overlay = img_color.copy()
        h, w = overlay.shape[:2]

        # pred may be the new output (with 'points' and 'vectors') or the older raw arrays.
        if isinstance(pred, dict) and "points" in pred and "vectors" in pred:
            points = pred["points"]
            vectors_map = pred["vectors"]

            # Draw centers
            for (x, y) in points.values():
                cx = int(round(x))
                cy = int(round(y))
                cv2.circle(overlay, (cx, cy), radius=4, color=point_color, thickness=-1)
                cv2.circle(overlay, (cx, cy), radius=7, color=(0, 0, 0), thickness=1)

            # Draw vectors directly from the precomputed "vectors" dict
            for key, (start_point, end_point) in vectors_map.items():
                if self.axis_repr.name in ["rho_theta", "rho_dir"]:
                    # For rho_theta or rho_dir, draw the full line clipped to image boundaries
                    direction_vec = (end_point[0] - start_point[0], end_point[1] - start_point[1])
                    p1, p2 = _clip_line_to_image(start_point, direction_vec, w, h)
                    if p1 and p2:
                        cv2.line(overlay, (int(round(p1[0])), int(round(p1[1]))), (int(round(p2[0])), int(round(p2[1]))), color=vector_color, thickness=2)
                else:
                    # For anchor_dir or other anchored vectors, draw an arrow from start to end
                    cv2.arrowedLine(overlay, (int(round(start_point[0])), int(round(start_point[1]))), (int(round(end_point[0])), int(round(end_point[1]))), color=vector_color, thickness=1, tipLength=0.1)
        else:
            # fallback to legacy format
            centers_px = pred.get("centers_px", np.zeros((0, 2), dtype=np.float32))
            vectors = pred.get("vectors_px", np.zeros((0, 2), dtype=np.float32))

            # Draw centers
            for (x, y) in centers_px:
                cx = int(round(x))
                cy = int(round(y))
                cv2.circle(overlay, (cx, cy), radius=4, color=point_color, thickness=-1)
                cv2.circle(overlay, (cx, cy), radius=7, color=(0, 0, 0), thickness=1)

            # Draw vectors anchored at axes anchors defined in meta['axes'] (list of (A,B))
            axes = self.meta.get("axes", [])
            landmarks = list(self.meta.get("landmarks", []))

            min_dim = min(w, h)
            Lpx = max(2, int(round(length_fraction * min_dim)))

            for i, vec in enumerate(vectors):
                # find anchor A for this axis in meta.axes; meta.axes is list of (A_name, B_name)
                if i >= len(axes):
                    # no anchor mapping — skip
                    continue
                A_name, _ = axes[i]
                # anchor index
                try:
                    anchor_idx = landmarks.index(A_name)
                except ValueError:
                    # try to match substrings (fallback)
                    anchor_idx = None
                    for j, nm in enumerate(landmarks):
                        if A_name.lower() in nm.lower() or nm.lower() in A_name.lower():
                            anchor_idx = j
                            break
                if anchor_idx is None or anchor_idx >= centers_px.shape[0]:
                    continue

                sx = int(round(centers_px[anchor_idx, 0]))
                sy = int(round(centers_px[anchor_idx, 1]))
                ex = int(round(sx + vec[0] * Lpx))
                ey = int(round(sy + vec[1] * Lpx))

                # draw arrowed line
                cv2.arrowedLine(overlay, (sx, sy), (ex, ey), color=vector_color, thickness=1, tipLength=0.1)

        # Save if requested
        if save_path:
            sp = Path(save_path)
            sp.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(sp), overlay)
            print(f"Saved visualization to: {sp}")

        # Show using matplotlib if requested
        if show and plt is not None:
            plt.figure(figsize=(8, 8))
            plt.imshow(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB))
            plt.axis("off")
            plt.tight_layout()
            plt.show()

        return overlay


if __name__ == "__main__":
    # Small example usage (edit paths as needed)
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("model", help="Path to trained landmark model (.pth)")
    parser.add_argument("image", help="Path to image to run inference on")
    parser.add_argument("--no-show", dest="show", action="store_false", help="Do not display with matplotlib")
    parser.add_argument("--save", help="Optional path to save overlay image")
    args = parser.parse_args()

    annotator = AnnotationModel(args.model)
    pred = annotator.predict(args.image, return_pixels=True)
    print("Predicted points:")
    for k, v in pred.get("points", {}).items():
        print(f"  {k}: {v}")
    print("\nPredicted vectors:")
    for k, v in pred.get("vectors", {}).items():
        print(f"  {k}: {v}")

    annotator.visualize(args.image, pred=pred, show=args.show, save_path=args.save)
