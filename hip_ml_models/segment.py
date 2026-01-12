"""
Modular segmentation wrapper for easy model loading, inference, and mask visualization/saving.

This module provides a clean interface to perform segmentation on images using a pre-trained model.
It handles model loading, image preprocessing, inference, and result visualization/saving.

Example usage:
    from segment import SegmentationModel
    
    # Initialize with model path
    segmenter = SegmentationModel(model_path="path/to/model/model_name.pth")
    
    # Predict on single image
    mask = segmenter.predict(image_path="path/to/image.png")
    
    # Visualize predictions
    segmenter.visualize_prediction(image_path="path/to/image.png", save_path="output.png")
    
    # Save mask(s)
    segmenter.save_masks(image_path="path/to/image.png", output_dir="path/to/output")

Dependencies:
    - torch 2.7.1+cu118
    - cv2
    - numpy
    - pillow
    - matplotlib (optional, for visualization)
"""

# import os
import torch
import torch.nn as nn
import cv2
import numpy as np
from pathlib import Path
from typing import Any, Union, Tuple, Optional, List
import warnings

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

TRAIN_TORCH_VERSION = "2.7.1+cu118"

# Ground-truth label mapping, they may be updated from a model checkpoint (see `_load_model`).
LABELS = {
    "_femur": "femur",
    "pelvis_mesh_hemi_": "pelvis",
    "pelvis_mesh_ramus_": "ramus",
    "_head": "head",
    "_cup": "cup",
    "_liner": "liner",
    "_stem": "stem",
}
# Masks used during training, they must be loaded from a model checkpoint (see `_load_model`)
GT_KEYS = ["_femur", "pelvis_mesh_ramus_"]

# ===============================
# Model (U-Net)
# ===============================
class AttentionGate(nn.Module):
    def __init__(self, F_g, F_l, F_int):
        super().__init__()
        self.W_g = nn.Sequential(
            nn.Conv2d(F_g, F_int, 1),
            nn.InstanceNorm2d(F_int)
        )
        self.W_x = nn.Sequential(
            nn.Conv2d(F_l, F_int, 1),
            nn.InstanceNorm2d(F_int)
        )
        self.psi = nn.Sequential(
            nn.Conv2d(F_int, 1, 1),
            nn.Sigmoid()
        )

    def forward(self, g, x):
        g1 = self.W_g(g)
        x1 = self.W_x(x)
        psi = torch.relu(g1 + x1)
        psi = self.psi(psi)
        return x * psi
    
class ConvBlock(nn.Module):
    def __init__(self, in_ch, out_ch, dropout=0.1):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.InstanceNorm2d(out_ch, affine=True), #  nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            
            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.InstanceNorm2d(out_ch, affine=True), # nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),

            nn.Dropout(dropout)
        )

    def forward(self, x):
        return self.block(x)

class UNet(nn.Module):
    def __init__(self, in_channels=1, out_channels=1, features=[64, 128, 256, 512]):
        super().__init__()
        self.downs = nn.ModuleList()
        self.ups = nn.ModuleList()
        self.attentions = nn.ModuleList()
        self.pool = nn.MaxPool2d(2)

        for feature in features:
            self.downs.append(ConvBlock(in_channels, feature))
            in_channels = feature

        for feature in reversed(features):
            self.ups.append(nn.ConvTranspose2d(feature * 2, feature, kernel_size=2, stride=2))
            self.ups.append(ConvBlock(feature * 2, feature))
            # Create an attention gate for this decoder level (gating channels == feature, skip channels == feature)
            self.attentions.append(AttentionGate(F_g=feature, F_l=feature, F_int=max(1, feature // 2)))

        self.bottleneck = ConvBlock(features[-1], features[-1] * 2)
        self.final_conv = nn.Conv2d(features[0], out_channels, kernel_size=1)

    def forward(self, x):
        skip_connections = []
        for down in self.downs:
            x = down(x)
            skip_connections.append(x)
            x = self.pool(x)

        x = self.bottleneck(x)
        skip_connections = skip_connections[::-1]

        for idx in range(0, len(self.ups), 2):
            x = self.ups[idx](x)
            skip_connection = skip_connections[idx // 2]
            if x.shape != skip_connection.shape:
                x = torch.nn.functional.interpolate(x, size=skip_connection.shape[2:], mode="bilinear", align_corners=True)
            # Apply attention gate to the skip connection using current decoder feature as gating signal
            if len(self.attentions) > 0:
                att = self.attentions[idx // 2]
                gated_skip = att(g=x, x=skip_connection)
            else:
                gated_skip = skip_connection
            concat_skip = torch.cat((gated_skip, x), dim=1)
            x = self.ups[idx + 1](concat_skip)

        return torch.sigmoid(self.final_conv(x))

class SegmentationModel:
    """
    A modular segmentation model wrapper for inference and visualization.
    
    This class handles:
    - Loading pre-trained segmentation models
    - Preprocessing images
    - Running inference on single images
    - Visualizing predictions with ground truth contours
    - Saving predicted masks in various formats
    
    Attributes:
        model: The loaded PyTorch model
        device: Compute device (cuda or cpu)
        image_size: Expected input size for the model (width, height)
        num_channels: Number of output channels (1 for femur, 2 for femur+pelvis, etc.)
    """
    
    def __init__(self, model_path: str, image_size: Tuple[int, int] = (256, 256), device: Optional[str] = None):
        """
        Initialize the segmentation model.
        
        NOTE: An explicit `model_path` to a model file is MANDATORY. There is no fallback
        search. If the file is missing or cannot be loaded an exception is raised.

        Args:
            model_path (str): Path to the model file to load (e.g. 'best_model.pth').
            image_size (tuple): Expected input image size as (width, height). Default: (256, 256)
            device (str, optional): Device to run model on ('cuda' or 'cpu'). 
                                   Auto-detects if None. Default: None
        
        Raises:
            FileNotFoundError: If `model_path` does not exist.
            RuntimeError: If model fails to load.

        Example:
            model = SegmentationModel(model_path="./segmentation/best_model_full.pth", image_size=(256,256))
        """

        if torch.__version__ != TRAIN_TORCH_VERSION:
            warnings.warn(f"PyTorch version mismatch detected! Training used torch=={TRAIN_TORCH_VERSION} | Inference is running torch=={torch.__version__}", UserWarning)

        self.model_path = Path(model_path)
        self.image_size = image_size
        self.device = self._select_device(device)
        self.model = None
        self.num_channels = None
        
        self._load_model()
        self._infer_num_channels()
        
    def _select_device(self, device: Optional[str] = None) -> torch.device:
        """
        Select compute device (CUDA if available, otherwise CPU).
        
        Args:
            device (str, optional): Explicit device choice ('cuda' or 'cpu')
            
        Returns:
            torch.device: Selected device
        """
        if not device:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        return torch.device(device)
    
    def _load_model(self) -> None:
        """
        Load pre-trained model from path.
        
        Loads the model state dictionary, input channels, and output channels from the model file:
        
        Raises:
            FileNotFoundError: If no model weights found
            RuntimeError: If model loading fails
        """
        # Load the required model file (no fallback search)
        model_path = self.model_path
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        try:
            # Load the model checkpoint metadata saved by torch.save
            
            checkpoint = torch.load(str(model_path), map_location=self.device)
            self.model = UNet(
                in_channels=checkpoint.get("in_channels", 1),
                out_channels=checkpoint.get("out_channels", 1)
            ).to(self.device)

            # Update global GT_KEYS and LABELS if checkpoint provides them
            global GT_KEYS, LABELS
            GT_KEYS = checkpoint.get("keys", GT_KEYS)

            # optional: allow checkpoints to ship a mapping of labels
            ck_labels = checkpoint.get("labels", None)
            if isinstance(ck_labels, dict):
                # merge/override defaults
                LABELS.update(ck_labels)
                
            self.num_channels = checkpoint.get("out_channels", 1)
            self.model.load_state_dict(checkpoint["model_state_dict"])

            self.model.eval()
            print(f"Segmentation model loaded from ({model_path}) to ({self.device}): {self.num_channels} output channels (masks).")
        except Exception as e:
            raise RuntimeError(f"Failed to load model from {model_path}: {e}")
    
    def _infer_num_channels(self) -> None:
        """
        Infer number of output channels by examining model architecture.
        
        For UNet models, checks the final output layer to determine if model
        outputs 1 channel (femur only) or 2+ channels (multi-organ).
        """
        if self.num_channels is not None:
            return  # Already set during loading
        try:
            # Try to access final conv layer output channels
            if hasattr(self.model, 'final_conv'):
                self.num_channels = self.model.final_conv.out_channels
            else:
                # Fallback: try a dummy forward pass with a small tensor
                with torch.no_grad():
                    dummy_input = torch.randn(1, 1, 32, 32).to(self.device)
                    dummy_output = self.model(dummy_input)
                    self.num_channels = dummy_output.shape[1]
            
            print(f"Model output channels: {self.num_channels}")
        except Exception as e:
            warnings.warn(f"Could not infer number of channels: {e}. Assuming 1 channel.")
            self.num_channels = 1
    
    def predict(
        self,
        image: Any,
        threshold: float = 0.5,
        return_probs: bool = False
    ) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """
        Run segmentation inference on a single image.
        
        Args:
            image_path (str or Path): Path to input image (grayscale or RGB)
            threshold (float): Binary threshold for mask (0.0-1.0). Default: 0.5
            return_probs (bool): If True, return both probabilities and binary mask.
                                If False, return only binary mask. Default: False
        
        Returns:
            np.ndarray: Binary mask (0/255) of shape (H, W) for single-channel or 
                       (C, H, W) for multi-channel models. Uint8 array.
            tuple: (probs, binary_mask) if return_probs=True. Probs are float32 [0..1],
                   binary masks are uint8 [0/255].
        
        Raises:
            FileNotFoundError: If image not found
            ValueError: If image cannot be processed
        
        Example:
            mask = model.predict("image.png", threshold=0.5)
            probs, mask_bin = model.predict("image.png", return_probs=True)
        """
        # Support multiple input types: Path/str, PIL.Image, numpy.ndarray, torch.Tensor
        pil_img = None

        # 1) Path / str
        if isinstance(image, (str, Path)):
            image_path = Path(image)
            if not image_path.exists():
                raise FileNotFoundError(f"Image not found: {image_path}")
            try:
                pil_img = Image.open(str(image_path)).convert("L")  # Grayscale
            except Exception as e:
                raise ValueError(f"Failed to load image {image_path}: {e}")

        # 2) PIL Image
        elif Image is not None and isinstance(image, Image.Image):
            pil_img = image.convert("L")

        # 3) torch.Tensor
        elif isinstance(image, torch.Tensor):
            t = image.detach().cpu().numpy()
            # if batch dimension present, take first
            if t.ndim == 4:
                t = t[0]
            # channels-first -> HWC
            if t.ndim == 3 and t.shape[0] in (1, 3, 4):
                t = np.transpose(t, (1, 2, 0))
            # scale floats [0..1] -> [0..255]
            if np.issubdtype(t.dtype, np.floating):
                t = np.clip(t, 0.0, 1.0)
                t = (t * 255.0).astype(np.uint8)
            else:
                t = t.astype(np.uint8)
            # convert to PIL (handle RGB/A -> grayscale)
            if t.ndim == 3 and t.shape[2] in (3, 4):
                try:
                    pil_img = Image.fromarray(cv2.cvtColor(t, cv2.COLOR_RGB2GRAY))
                except Exception:
                    pil_img = Image.fromarray(t[..., :3].mean(axis=2).astype(np.uint8))
            elif t.ndim == 2:
                pil_img = Image.fromarray(t)
            else:
                raise ValueError(f"Unsupported tensor image shape: {t.shape}")

        # 4) numpy.ndarray
        elif isinstance(image, np.ndarray):
            arr = image
            # channels-first -> HWC
            if arr.ndim == 3 and arr.shape[0] in (1, 3, 4) and arr.shape[0] < arr.shape[1]:
                arr = np.transpose(arr, (1, 2, 0))
            # scale floats
            if np.issubdtype(arr.dtype, np.floating):
                arr = np.clip(arr, 0.0, 1.0)
                arr = (arr * 255.0).astype(np.uint8)
            else:
                arr = arr.astype(np.uint8)
            if arr.ndim == 3 and arr.shape[2] in (3, 4):
                try:
                    pil_img = Image.fromarray(cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY))
                except Exception:
                    pil_img = Image.fromarray(arr[..., :3].mean(axis=2).astype(np.uint8))
            elif arr.ndim == 2:
                pil_img = Image.fromarray(arr)
            else:
                raise ValueError(f"Unsupported numpy image shape: {arr.shape}")

        else:
            raise TypeError("Unsupported input type for predict(). Accepts path (str/Path), PIL.Image, numpy.ndarray, or torch.Tensor")
        
        # Prepare input tensor (pil_img is grayscale PIL.Image at this point)
        input_tensor = self._preprocess_image(pil_img)
        
        # Run inference
        with torch.no_grad():
            output = self.model(input_tensor)
        
        # Post-process output
        output_np = output.cpu().squeeze().numpy().astype(np.float32)
        
        # Handle single vs multi-channel outputs
        if output_np.ndim == 2:
            # Single channel: (H, W)
            probs = cv2.resize(output_np, self.image_size, interpolation=cv2.INTER_LINEAR)
        else:
            # Multi-channel: (C, H, W)
            probs_list = [
                cv2.resize(output_np[c], self.image_size, interpolation=cv2.INTER_LINEAR)
                for c in range(output_np.shape[0])
            ]
            probs = np.stack(probs_list, axis=0)
        
        # Binarize
        binary_mask = (probs >= threshold).astype(np.uint8) * 255
        
        if return_probs:
            return probs, binary_mask
        return binary_mask
    
    def _preprocess_image(self, pil_img) -> torch.Tensor:
        """
        Preprocess PIL image to model input tensor.
        
        Converts to correct size and normalizes to [0, 1].
        
        Args:
            pil_img (PIL.Image): Grayscale PIL image
            
        Returns:
            torch.Tensor: Input tensor of shape (1, 1, H, W) on correct device
        """
        # Resize to model input size
        pil_resized = pil_img.resize(self.image_size, Image.BILINEAR)
        
        # Convert to numpy and normalize
        arr = np.asarray(pil_resized).astype(np.float32) / 255.0
        
        # Add batch and channel dims: (H, W) -> (1, 1, H, W)
        tensor = torch.from_numpy(arr)[None, None, ...].float()
        tensor = tensor.to(self.device)
        
        return tensor
    
    def visualize_prediction(
        self,
        image_path: Union[str, Path],
        threshold: float = 0.5,
        save_path: Optional[Union[str, Path]] = None,
        show: bool = True,
        contour_color: str = "green"
    ) -> Optional[np.ndarray]:
        """
        Visualize predicted mask overlaid on original image.
        
        Draws predicted contours on the image and optionally saves/displays result.
        Supports both single-channel (femur) and multi-channel (femur+pelvis) predictions.
        
        Args:
            image_path (str or Path): Path to input image
            threshold (float): Binary threshold for mask. Default: 0.5
            save_path (str or Path, optional): Path to save visualization. Default: None (no save)
            show (bool): Display visualization using matplotlib. Default: True
            contour_color (str): Contour color ('green', 'red', 'blue', etc.). Default: 'green'
        
        Returns:
            np.ndarray: Visualization image as BGR numpy array, or None if plt not available
        
        Example:
            model.visualize_prediction("image.png", save_path="output.png", show=True)
        """
        image_path = Path(image_path)
        
        # Load original image
        try:
            original_pil = Image.open(str(image_path)).convert("RGB")
        except Exception as e:
            raise ValueError(f"Failed to load image {image_path}: {e}")
        
        original_bgr = cv2.cvtColor(np.asarray(original_pil), cv2.COLOR_RGB2BGR)
        
        # Get prediction
        probs, binary_mask = self.predict(image_path, threshold=threshold, return_probs=True)
        
        # Resize masks to original image size
        orig_h, orig_w = original_bgr.shape[:2]
        
        if binary_mask.ndim == 2:
            # Single channel
            mask_resized = cv2.resize(binary_mask, (orig_w, orig_h), interpolation=cv2.INTER_NEAREST)
            masks_list = [mask_resized]
        else:
            # Multi-channel
            masks_list = [
                cv2.resize(binary_mask[c], (orig_w, orig_h), interpolation=cv2.INTER_NEAREST)
                for c in range(binary_mask.shape[0])
            ]
        
        # Draw contours on overlay
        overlay_bgr = original_bgr.copy()
        color_map = {
            "green": (0, 255, 0),
            "red": (0, 0, 255),
            "blue": (255, 0, 0),
            "yellow": (0, 255, 255),
            "cyan": (255, 255, 0),
            "magenta": (255, 0, 255),
        }
        color_bgr = color_map.get(contour_color.lower(), (0, 255, 0))
        
        for mask in masks_list:
            cnts, _ = cv2.findContours(mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(overlay_bgr, cnts, -1, color_bgr, thickness=2)
        
        # Save if requested
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(save_path), overlay_bgr)
            print(f"Visualization saved to: {save_path}")
        
        # Display if requested and matplotlib available
        if show and plt is not None:
            plt.figure(figsize=(10, 8))
            plt.imshow(cv2.cvtColor(overlay_bgr, cv2.COLOR_BGR2RGB))
            plt.title(f"Prediction (threshold={threshold})")
            plt.axis("off")
            plt.tight_layout()
            plt.show()
        
        return overlay_bgr
    
    def save_masks(
        self,
        image_path: Union[str, Path],
        output_dir: Union[str, Path],
        threshold: float = 0.5,
        labels: Optional[List[str]] = None
    ) -> List[Path]:
        """
        Save predicted mask(s) to output directory.
        
        Handles both single-channel and multi-channel predictions:
        - Single-channel: Saves as "{image_stem}_mask.png"
        - Multi-channel: Saves as "{image_stem}_{label}.png" for each channel
        
        Args:
            image_path (str or Path): Path to input image
            output_dir (str or Path): Directory to save masks
            threshold (float): Binary threshold for mask. Default: 0.5
            labels (list, optional): Channel labels for multi-channel output.
                                    Default: ['femur', 'pelvis'] for 2-channel, etc.
        
        Returns:
            list: List of Path objects for saved files
        
        Example:
            paths = model.save_masks("image.png", "output_dir", threshold=0.5)
            for p in paths:
                print(f"Saved: {p}")
        """
        image_path = Path(image_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get prediction
        binary_mask = self.predict(image_path, threshold=threshold, return_probs=False)
        
        # Prepare labels
        labels = [LABELS[m] for m in GT_KEYS if m in LABELS]
        
        # Save masks
        saved_paths = []
        image_stem = image_path.stem
        
        if binary_mask.ndim == 2:
            # Single channel
            out_path = output_dir / f"{image_stem}_mask.png"
            cv2.imwrite(str(out_path), binary_mask)
            saved_paths.append(out_path)
            print(f"Saved mask to: {out_path}")
        else:
            # Multi-channel
            for c, label in enumerate(labels[:binary_mask.shape[0]]):
                out_path = output_dir / f"{image_stem}_{label}.png"
                cv2.imwrite(str(out_path), binary_mask[c])
                saved_paths.append(out_path)
                print(f"Saved {label} mask to: {out_path}")
        
        return saved_paths
    
    def batch_process(
        self,
        image_dir: Union[str, Path],
        output_dir: Union[str, Path],
        threshold: float = 0.5,
        extensions: Tuple[str, ...] = (".png", ".jpg", ".jpeg", ".bmp")
    ) -> List[Path]:
        """
        Process all images in a directory and save masks.
        
        Args:
            image_dir (str or Path): Directory containing images
            output_dir (str or Path): Directory to save output masks
            threshold (float): Binary threshold. Default: 0.5
            extensions (tuple): Supported image extensions. Default: common formats
        
        Returns:
            list: List of all saved mask file paths
        
        Example:
            all_masks = model.batch_process("images/", "masks/", threshold=0.5)
        """
        image_dir = Path(image_dir)
        if not image_dir.is_dir():
            raise NotADirectoryError(f"Not a directory: {image_dir}")
        
        # Find all images
        image_files = [
            f for f in image_dir.rglob("*")
            if f.is_file() and f.suffix.lower() in extensions
        ]
        
        if not image_files:
            warnings.warn(f"No images found in {image_dir}")
            return []
        
        print(f"Processing {len(image_files)} images...")
        all_saved = []
        
        for i, img_path in enumerate(image_files, 1):
            try:
                saved = self.save_masks(img_path, output_dir, threshold=threshold)
                all_saved.extend(saved)
                print(f"  [{i}/{len(image_files)}] - saved {img_path.name}")
            except Exception as e:
                print(f"  [{i}/{len(image_files)}] - {img_path.name} not saved: {e}")
        
        print(f"Batch processing complete. Saved {len(all_saved)} masks.")
        return all_saved


# Example usage / testing
if __name__ == "__main__":
    # Example: Initialize and use the segmentation model
    
    # 1. Initialize model 
    seg_model = SegmentationModel(model_path="path/to_model/NoChannels_model_name.pth", image_size=(256, 256))
    
    # 2. Predict on single image
    image_path = r"path/to/image.png"
    try:
        mask = seg_model.predict(image_path, threshold=0.5)
        print(f"Prediction shape: {mask.shape}")
        
        # 3. Visualize prediction
        seg_model.visualize_prediction(image_path, threshold=0.5, save_path="pred_viz.png", show=False)
        
        # 4. Save mask
        output_dir = "./predictions"
        saved_paths = seg_model.save_masks(image_path, output_dir, threshold=0.5)
        print(f"Saved {len(saved_paths)} mask file(s)")
        
    except Exception as e:
        print(f"Example failed: {e}")
