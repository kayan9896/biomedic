"""
Unified wrapper for THA classification, segmentation, and annotation models.

This module provides a single class: `HipModels`, which handles:
    • Loading all 7 models OR a single-phase subset of them.
    • Unified calls: classify(), segment(), annotate()
    • Automatic left/right flipping using the classification model
    • Automatic “no-hip” rejection if enabled

Models expected (default names):
    class_model.pth
    ref_seg_model.pth
    cup_seg_model.pth
    trial_seg_model.pth
    ref_lm_model.pth
    cup_lm_model.pth
    trial_lm_model.pth

Code by Maad Ebrahim for Torus Biomedical Inc., 2025-2027.
    
Phases:
    phase = "all" | "ref" | "cup" | "trial"

Dependencies:
    classify.py     → ClassificationModel
    segment.py      → SegmentationModel
    annotate.py     → AnnotationModel
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Any, Dict, Union
from confirmap_dataclasses import *
import warnings
import numpy as np
import cv2

try:
    from .classify import ClassificationModel
    from .segment import SegmentationModel
    from .annotate import AnnotationModel
    # from .onnx_exporter import export_pth_to_onnx
except ImportError:
    from classify import ClassificationModel
    from segment import SegmentationModel
    from annotate import AnnotationModel
    # from onnx_exporter import export_pth_to_onnx

from dataclasses import dataclass
from pathlib import Path

@dataclass(slots=True)
class HipModelConfig:
    model_dir: Union[str, Path] = r"\\Torus-NAS\Torus-Data\models"

    later_cls_name: str = "later_class_model.pth"
    phase_cls_name: str = "phase_class_model.pth"

    ref_seg_name: str = "ref_seg_model.pth"
    cup_seg_name: str = "cup_seg_model.pth"
    trial_seg_name: str = "trial_seg_model.pth"

    ref_lm_name: str = "ref_lm_model.pth"
    cup_lm_name: str = "cup_lm_model.pth"
    trial_lm_name: str = "trial_lm_model.pth"

    phase: str = "ref"   # "all", "ref", "cup", "trial"

    # ---- helpers ----
    def seg_name(self, phase: str) -> str:
        return getattr(self, f"{phase}_seg_name")

    def lm_name(self, phase: str) -> str:
        return getattr(self, f"{phase}_lm_name")
    
    def __post_init__(self):
        self.model_dir = Path(self.model_dir)

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def get_image_size(img):
    """Get (height, width) of input image (path / PIL / numpy / tensor)."""

    # NumPy array
    if isinstance(img, np.ndarray):
        if img.ndim == 2:          # (H, W)
            return img.shape
        elif img.ndim == 3:        # (H, W, C) or (C, H, W)
            # Heuristic: assume channels-last if last dim is small
            if img.shape[-1] in (1, 3, 4):
                return img.shape[0], img.shape[1]
            else:                  # channels-first
                return img.shape[1], img.shape[2]

    # Path / string → load with OpenCV
    if isinstance(img, (str, Path)):
        arr = cv2.imread(str(img), cv2.IMREAD_GRAYSCALE)
        if arr is None:
            raise ValueError(f"Failed to read image: {img}")
        return arr.shape  # (H, W)

    # PIL Image
    try:
        from PIL import Image
        if isinstance(img, Image.Image):
            return img.height, img.width
    except Exception:
        pass

    # Torch tensor
    try:
        import torch
        if isinstance(img, torch.Tensor):
            if img.dim() == 2:      # (H, W)
                return img.size(0), img.size(1)
            elif img.dim() == 3:    # (C, H, W)
                return img.size(1), img.size(2)
    except Exception:
        pass

    raise TypeError(f"Unsupported image type for getting size: {type(img)}")


def flip_image(img: Any) -> Any:
    """Flip an input *path / PIL / numpy / tensor* horizontally, preserving type."""
    # For numpy case
    if isinstance(img, np.ndarray):
        return np.flip(img, axis=1).copy()

    # For cv2 path → load, flip, return numpy
    if isinstance(img, (str, Path)):
        arr = cv2.imread(str(img), cv2.IMREAD_GRAYSCALE)
        if arr is None:
            raise ValueError(f"Failed to read image: {img}")
        return np.flip(arr, axis=1).copy()

    # PIL
    try:
        from PIL import Image
        if isinstance(img, Image.Image):
            return img.transpose(Image.FLIP_LEFT_RIGHT)
    except Exception:
        pass

    # Torch tensor
    try:
        import torch
        if isinstance(img, torch.Tensor):
            # Flip width dimension
            if img.dim() >= 3:
                return torch.flip(img, dims=[-1])
    except Exception:
        pass

    raise TypeError(f"Unsupported image type for flipping: {type(img)}")


def flip_annotation_output(pred, img_width=1.0):
    """Flip annotation output dict back horizontally."""
    # pred = {"points": {...}, "vectors": {...}}
    out = {"points": {}, "vectors": {}}

    # Flip points
    for k, (x, y) in pred["points"].items():
        out["points"][k] = (img_width-x, y)  # x becomes mirrored (negated in normalized/pixel coords)

    # Flip vectors: anchor & end must flip their x-coordinates
    for k, (a, b) in pred["vectors"].items():
        ax, ay = a
        bx, by = b
        out["vectors"][k] = ((img_width-ax, ay), (img_width-bx, by))

    return out


def flip_segmentation_output(mask: np.ndarray) -> np.ndarray:
    """Flip segmentation mask horizontally."""
    if mask.ndim == 2:
        return np.flip(mask, axis=1).copy()
    elif mask.ndim == 3:
        return np.flip(mask, axis=2).copy()   # (C, H, W)
    else:
        raise ValueError("Unsupported segmentation mask shape.")


def hip_config_from_frame_prediction(cfg: FramePredictionConfigClass) -> HipModelConfig:
    """
    Convert ConfirMap FramePredictionConfigClass → HipModelConfig
    """
    def _name(p: Path | None, default: str) -> str:
        return p.name if p is not None else default

    def _dir(p: Path | None, default: Path) -> Path:
        return p.parent if p is not None else default

    model_dir = _dir(cfg.classifier_model_path, Path(r"\\Torus-NAS\Torus-Data\models"))

    return HipModelConfig(
        model_dir=model_dir,

        later_cls_name=_name(cfg.classifier_model_path, "later_class_model.pth"),

        ref_seg_name=_name(cfg.ref_segmentor_model_path, "ref_seg_model.pth"),
        cup_seg_name=_name(cfg.cup_segmentor_model_path, "cup_seg_model.pth"),
        trial_seg_name=_name(cfg.trl_segmentor_model_path, "trial_seg_model.pth"),

        ref_lm_name=_name(cfg.ref_annotator_model_path, "ref_lm_model.pth"),
        cup_lm_name=_name(cfg.cup_annotator_model_path, "cup_lm_model.pth"),
        trial_lm_name=_name(cfg.trl_annotator_model_path, "trial_lm_model.pth"),
    )


def dice_coeff(a: np.ndarray, b: np.ndarray, eps: float = 1e-6) -> float:
    a = a.astype(bool)
    b = b.astype(bool)
    inter = np.logical_and(a, b).sum()
    return (2.0 * inter + eps) / (a.sum() + b.sum() + eps)


def keep_largest_cc(mask: np.ndarray) -> np.ndarray:
    num, labels = cv2.connectedComponents(mask.astype(np.uint8))
    if num <= 1:
        return mask
    largest = max(range(1, num), key=lambda i: (labels == i).sum())
    return (labels == largest).astype(np.uint8)


def segmentation_stability_confidence(
    probs: np.ndarray,
    thresholds=(0.001, 0.999),
    postprocess=True,
) -> float:
    masks = []
    for t in thresholds:
        m = (probs > t).astype(np.uint8)
        if postprocess:
            m = keep_largest_cc(m)
        masks.append(m)

    dices = []
    for i in range(len(masks)):
        for j in range(i + 1, len(masks)):
            dices.append(dice_coeff(masks[i], masks[j]))

    return float(np.mean(dices)) if dices else 0.0

# ---------------------------------------------------------------------------
# HipModels (Main class)
# ---------------------------------------------------------------------------

class HipModels:
    """
    Unified wrapper around:
        - ClassificationModel
        - SegmentationModel (ref/cup/trial)
        - AnnotationModel (ref/cup/trial)

    Args:
        model_dir (str): Base directory containing all model .pth files.
        later_cls_name (str)
        ref_seg_name, cup_seg_name, trial_seg_name
        ref_lm_name, cup_lm_name, trial_lm_name
        phase (str): "all", "ref", "cup", or "trial"

    Usage:
        m = HipModels()
        cls = m.classify(image)
        seg = m.segment(image, phase="cup")
        ann = m.annotate(image, phase="ref")
    """

    def __init__(
        self,
        *,
        config: HipModelConfig | None = None,
        frame_config: FramePredictionConfigClass | None = None,
        device: Optional[str] = None,
    ):
        if config is not None and frame_config is not None:
            warnings.warn("Can't initialize with both config and frame_config, using frame_config..")
            config = hip_config_from_frame_prediction(frame_config)

        if frame_config is not None:
            config = hip_config_from_frame_prediction(frame_config)

        if config is None:
            config = HipModelConfig()
        self.config = config
        self.model_dir = config.model_dir
        self.phase = config.phase
        self.device = device

        # -----------------------------
        # Load classification model
        # -----------------------------
        self.classifier = ClassificationModel(str(self.model_dir / config.later_cls_name), device=device)

        # -----------------------------
        # Load segmentation models
        # -----------------------------
        self.seg_models: Dict[str, Optional[SegmentationModel]] = {
            "ref": None, "cup": None, "trial": None
        }

        for p in ["ref", "cup", "trial"]:
            if self.phase in ("all", p):
                self.seg_models[p] = SegmentationModel(
                    str(self.model_dir / config.seg_name(p)),
                    device=device,
                )

        # -----------------------------
        # Load annotation models
        # -----------------------------
        self.lm_models: Dict[str, Optional[AnnotationModel]] = {
            "ref": None, "cup": None, "trial": None
        }

        for p in ["ref", "cup", "trial"]:
            if self.phase in ("all", p):
                self.lm_models[p] = AnnotationModel(
                    str(self.model_dir / config.lm_name(p)),
                    device=device,
                )

    # ----------------------------------------------------------------------
    # Helper: update phase (if new phase is all load all if not loaded already, if new phase is single load it if not loaded and unload others if loaded)
    # ----------------------------------------------------------------------
    def update_phase(self, new_phase: str):
        """
        Update the phase of the models.

        Args:
            new_phase (str): "all", "ref", "cup", or "trial"
        """
        if new_phase == self.phase:
            return  # No change

        self.phase = new_phase
        cfg = self.config


        # Segmentation models
        for p in ["ref", "cup", "trial"]:
            if new_phase in ("all", p):
                if self.seg_models[p] is None:
                    self.seg_models[p] = SegmentationModel(
                        str(self.model_dir / cfg.seg_name(p)),
                        device=self.device,
                    )
            else:
                self.seg_models[p] = None  # unload

        # Annotation models
        for p in ["ref", "cup", "trial"]:
            if new_phase in ("all", p):
                if self.lm_models[p] is None:
                    self.lm_models[p] = AnnotationModel(
                        str(self.model_dir / cfg.lm_name(p)),
                        device=self.device,
                    )
            else:
                self.lm_models[p] = None  # unload

    # ----------------------------------------------------------------------
    # 1) Classification wrapper
    # ----------------------------------------------------------------------
    def classify(self, image: Any, *, human_readable: bool = False, **kwargs):
        """
        Classification wrapper.

        By default this calls `self.classifier.predict()` and returns the numeric
        label (0=RIGHT, 1=LEFT, 2=NO-HIP). If `human_readable=True` this will call
        `self.classifier.predict_with_names()` and return the human-readable result
        from that method.

        Args:
            image: Input image (path / array / PIL / tensor).
            human_readable: If True, call `predict_with_names` instead of `predict`.
            **kwargs: Passed through to the underlying classifier method.

        Returns:
            Depends on the underlying method: integer label or human-readable output.
        """
        if human_readable:
            return self.classifier.predict_with_names(image, **kwargs)

        return self.classifier.predict(image, **kwargs)

    # ----------------------------------------------------------------------
    # Helper: determine laterality + flip
    # ----------------------------------------------------------------------
    def _determine_flip(self, image: Any, flip_if_left: bool, only_if_hip: bool):
        """
        Returns:
            (laterality, image2)

            laterality ∈ {0 (right), 1 (left), 2 (no hip)}
            image2     = flipped copy of input image if needed
        """
        laterality = self.classifier.predict(image)

        # If no-hip → return None?
        if laterality == 2 and only_if_hip:
            return laterality, None

        if laterality == 1 and flip_if_left:  # LEFT HIP
            return laterality, flip_image(image)

        return laterality, image

    # ----------------------------------------------------------------------
    # 2) Segmentation wrapper
    # ----------------------------------------------------------------------
    def segment(
        self,
        image: Any,
        *,
        phase: str,
        threshold: float = 0.5,
        flip_if_left: bool = True,
        only_if_hip: bool = True,
        return_probs: bool = False,
    ):
        """
        Segment hip structures for a given phase ("ref", "cup", "trial").

        Flips left hips before inference, unflips output afterward.
        Rejects no-hip images if only_if_hip=True.
        """
        if self.seg_models.get(phase) is None:
            raise ValueError(f"Segmentation model for phase '{phase}' not loaded.")

        laterality, img2 = self._determine_flip(image, flip_if_left, only_if_hip)
        if img2 is None:    # no hip
            return None

        seg_model = self.seg_models[phase]
        result = seg_model.predict(img2, threshold=threshold, return_probs=return_probs)

        # Flip back if original was left
        if laterality == 1 and flip_if_left:
            if return_probs:
                probs, mask = result
                return flip_segmentation_output(probs), flip_segmentation_output(mask)
            else:
                return flip_segmentation_output(result)

        if return_probs:
            probs, mask = result
            return probs, mask
        else:
            return result

    # ----------------------------------------------------------------------
    # 3) Annotation wrapper
    # ----------------------------------------------------------------------
    def annotate(
        self,
        image: Any,
        *,
        phase: str,
        flip_if_left: bool = True,
        only_if_hip: bool = True,
        return_pixels: bool = True,
        **kwargs
    ):
        """
        Predict anatomical landmarks + axes for a given phase.

        Automatically flips left images before inference and flips outputs back.
        Rejects 'no-hip' images if only_if_hip=True.

        Returns:
            {"points": {...}, "vectors": {...}}  OR  None
        """
        if self.lm_models.get(phase) is None:
            raise ValueError(f"Annotation model for phase '{phase}' not loaded.")

        laterality, img2 = self._determine_flip(image, flip_if_left, only_if_hip)
        if img2 is None:
            return None

        lm_model = self.lm_models[phase]
        pred = lm_model.predict(img2, return_pixels=return_pixels, **kwargs)

        # get the width of the image for flipping points (consider return_pixels is True/False)
        if return_pixels:
            img_height, img_width = get_image_size(img2)
        else:
            img_width = 1.0  # normalized coords in [0, 1]

        # flip output back
        if laterality == 1 and flip_if_left:
            return flip_annotation_output(pred, img_width)

        return pred

    # ---------------------------------------------------------------------------
    # 4) a unified predict() method (classify side + classify phase (currently return the current phase as such model is not implemented) + segment + annotate)
    # ---------------------------------------------------------------------------
    def predict(
        self,
        image: Any | None = None,
        *,
        frame: Frame | None = None,
        phase: str | None = None,
        seg_threshold: float = 0.5,
        seg_flip_if_left: bool = True,
        seg_only_if_hip: bool = False,
        ann_flip_if_left: bool = True,
        ann_only_if_hip: bool = False,
        ann_return_pixels: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Unified predict method: classify + segment + annotate.

        Returns a dict with keys:
            "laterality": int
            "segmentation": np.ndarray or None
            "annotation": dict or None
        """

        # Resolve inputs (Frame-based OR legacy)
        if frame is not None:
            if image is not None:
                warnings.warn("Both frame and image provided, ignoring image and using frame.meta.image_filename instead.")

            # Image
            image = frame.meta.image_filename
            if image is None:
                image = frame.image
                if image is None:
                    raise ValueError("Frame.meta.image_filename and Frame.image are None, cannot proceed.")

            # Phase (priority order)
            if phase is None:
                phase = "cup" if "cup" in frame.meta.op_stage else "trial" if "tri" in frame.meta.op_stage else "ref"

        else:
            # Legacy mode
            if image is None:
                raise ValueError("Either image or frame must be provided")

            if phase is None:
                raise ValueError("phase must be provided when using image input")


        output: Dict[str, Any] = {}

        if phase != self.phase:
            self.update_phase(phase)

        # 1) Classify
        laterality, probability = self.classify(image, human_readable=True, return_probs=True)
        output["laterality_name"] = laterality
        output["laterality_probs"] = probability
        output["phase"] = phase

        # 2) Segment
        probs, masks_bin = self.segment(
            image,
            phase=phase,
            threshold=seg_threshold,
            flip_if_left=seg_flip_if_left,
            only_if_hip=seg_only_if_hip,
            return_probs=True
        )
        output["segmentation"] = masks_bin if masks_bin is not None else None
        output["segmentation_probs"] = probs if probs is not None else None

        # 3) Annotate
        annot = self.annotate(
            image,
            phase=phase,
            flip_if_left=ann_flip_if_left,
            only_if_hip=ann_only_if_hip,
            return_pixels=ann_return_pixels,
            **kwargs
        )
        
        output["annotation_points"] = annot["points"] if annot is not None else None
        output["annotation_vectors"] = annot["vectors"] if annot is not None else None

        output["success"] = True if (masks_bin is not None and annot is not None) else False

        landmarks = [
            # Femur points
            "_neck center",
            "_piriformis entry point",
            "_head_center",
            "_lesser_trochanter_point_on_mesh",
            "_lesser_trochanter_point_on_shaft",
            "_neck_axis_inferior_point",
            "_neck_axis_superior_point",
            "_neck_shaft_ap_intersection_point_on_neck_axis",
            "_neck_shaft_ap_intersection_point_on_shaft_axis",
            # Pelvis points
            "_pt",
            "_p1",
            "_p2",
            "_p3",
            "_p4",
            "_p5",
            "_p6",
            "_p7",
            "_p8",
            "_extracted_teardrop",
            # cup points
            "cup_origin",
            "cup_top",
        ]

        axes = {
            ("_head_center", "_neck_axis_inferior_point"): "Femur Neck axis",  
            ("_lesser_trochanter_point_on_shaft", "_shaft_spline_proximal_point") : "Femur Shaft axis",  
            ("_lesser_trochanter_point_on_mesh", "_lesser_trochanter_point_on_shaft"): "Lesser Trochanter axis",  
            ("_head_center", "pelvis_center"): "Pelvis Orientation axis",  
        }

        # Landmark groups (femur points and axes, pelvis points and axes, cup points and axes, implanted head points and axes)
        landmark_groups = {
            "femur_1": {
                "points": landmarks[:9],
                "axes": list(axes.keys()),
            },
            "pelvis_1": {
                "points": landmarks[9:19],
                "axes": [],
            },
            "cup": {
                "points": landmarks[19:],
                "axes": [],
            },
            "implanted head": {
                "points": [],
                "axes": [],
            },
        }

        ann = FrameAnnotation(
            datasource="model",
            version="v1",
            side=None if output["laterality_name"] == "NO-HIP" else output["laterality_name"].split(' ')[0].lower(),
            success=output["success"],
            error_code=None,
            tags={"phase": output["phase"], "side classification": output["laterality_name"], "classification confidence": output["laterality_probs"]},
        )

        landmarks = LandmarksData()

        # Get image size to determine if points are visible (inside image)
        img_height, img_width = get_image_size(image)

        for group_name, items in landmark_groups.items():
            group = LandmarkGroup()
            # Points
            for point_name in items["points"]:
                if output["annotation_points"] is not None and point_name in output["annotation_points"]:
                    x, y = output["annotation_points"][point_name]
                    group.items[point_name] = LandmarkData(
                        label=point_name,
                        type="point",
                        coords=[(float(x), float(y))],
                        confidence=[None],
                        visible=0.0 <= x <= img_width and 0.0 <= y <= img_height,
                    )
            # Axes
            for a, b in items["axes"]:
                if output["annotation_vectors"] is not None and (a, b) in output["annotation_vectors"]:
                    ax, ay = output["annotation_vectors"][(a, b)][0]
                    bx, by = output["annotation_vectors"][(a, b)][1]
                    group.items[axes[(a, b)]] = LandmarkData(
                        label=f"{a}->{b}",
                        type="line",
                        coords=[(float(ax), float(ay)), (float(bx), float(by))],
                        confidence=[None, None],
                        visible=True,
                    )
            if group.items:
                landmarks.groups[group_name] = group


        # # Landmarks
        # if output["annotation_points"] is not None:
        #     group = LandmarkGroup()
        #     for k, (x, y) in output["annotation_points"].items():
        #         group.items[k] = LandmarkData(
        #             label=k,
        #             type="point",
        #             coords=[(float(x), float(y))],
        #             confidence=[None],
        #             visible=0.0 <= x <= img_width and 0.0 <= y <= img_height,
        #         )
        #     landmarks.groups["points"] = group

        # # Vectors
        # if output["annotation_vectors"] is not None:
        #     group = LandmarkGroup()
        #     for k, (a, b) in output["annotation_vectors"].items():
        #         ax, ay = a
        #         bx, by = b
        #         group.items[str(k)] = LandmarkData(
        #             label=str(k),
        #             type="line",
        #             coords=[(float(ax), float(ay)), (float(bx), float(by))],
        #             confidence=[None, None],
        #             visible=True,
        #         )
        #     landmarks.groups["vectors"] = group
        
        ann.landmarks = landmarks

        ann.masks = MasksData()

        # Masks
        if output["segmentation"] is not None:
            for k, mask in output["segmentation"].items():
                ann.masks.items[k] = MaskData(
                    label=k,
                    type="mask",
                    data = mask,
                    confidence=[segmentation_stability_confidence(probs=output["segmentation_probs"][k])],  # prediction reliability
                )
        
        return ann
    
    
#     # ----------------------------------------------------------------------
#     # Export all loaded models to ONNX (with metadata if available)
#     # ----------------------------------------------------------------------
#     def export_loaded_models_to_onnx(
#         self,
#         *,
#         output_dir: Optional[Union[str, Path]] = None,
#         overwrite: bool = False,
#     ):
#         """
#         Export all currently loaded models to ONNX format, embedding
#         checkpoint metadata verbatim.

#         Only models that are currently loaded (based on phase) are exported.

#         Args:
#             output_dir: Directory to write ONNX files to.
#                         Defaults to model_dir if None.
#             overwrite: Whether to overwrite existing .onnx files.
#         """
#         output_dir = Path(output_dir) if output_dir else self.model_dir
#         output_dir.mkdir(parents=True, exist_ok=True)

#         exports = []

#         # -----------------------------
#         # Classification model
#         # -----------------------------
#         cls_pth = self.model_dir / self.config.later_cls_name
#         cls_onnx = output_dir / cls_pth.with_suffix(".onnx").name

#         if overwrite or not cls_onnx.exists():
#             export_pth_to_onnx(
#                 model_wrapper=ClassificationModel,
#                 pth_path=str(cls_pth),
#                 onnx_path=str(cls_onnx),
#             )
#             exports.append(cls_onnx)

#         # -----------------------------
#         # Segmentation models
#         # -----------------------------
#         for phase, model in self.seg_models.items():
#             if model is None:
#                 continue

#             pth_path = self.model_dir / self.config.seg_name(phase)
#             onnx_path = output_dir / pth_path.with_suffix(".onnx").name

#             if overwrite or not onnx_path.exists():
#                 export_pth_to_onnx(
#                     model_wrapper=SegmentationModel,
#                     pth_path=str(pth_path),
#                     onnx_path=str(onnx_path),
#                 )
#                 exports.append(onnx_path)

#         # -----------------------------
#         # Annotation / landmark models
#         # -----------------------------
#         for phase, model in self.lm_models.items():
#             if model is None:
#                 continue

#             pth_path = self.model_dir / self.config.lm_name(phase)
#             onnx_path = output_dir / pth_path.with_suffix(".onnx").name

#             if overwrite or not onnx_path.exists():
#                 export_pth_to_onnx(
#                     model_wrapper=AnnotationModel,
#                     pth_path=str(pth_path),
#                     onnx_path=str(onnx_path),
#                 )
#                 exports.append(onnx_path)

#         return exports

# if __name__ == "__main__":
#     # export to onnx test
#     cfg = HipModelConfig()

#     models = HipModels(config=cfg)
#     onnx_files = models.export_loaded_models_to_onnx(overwrite=True)