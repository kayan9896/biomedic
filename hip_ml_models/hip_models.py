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

    phase: str = "all"   # "all", "ref", "cup", "trial"

    # ---- helpers ----
    def seg_name(self, phase: str) -> str:
        return getattr(self, f"{phase}_seg_name")

    def lm_name(self, phase: str) -> str:
        return getattr(self, f"{phase}_lm_name")
    
    def __post_init__(self):
        self.model_dir = Path(self.model_dir)
    

# create a dataclass for the predict() method
@dataclass(slots=True)
class HipModelPrediction:
    laterality_name: str
    laterality_probs: Dict[str, float]
    phase: str
    segmentation: Optional[np.ndarray]
    annotation_points: Optional[Dict[str, Any]]
    annotation_vectors: Optional[Dict[str, Any]]
    success: bool

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

# define a helper to get the width of the image for flipping points
def get_image_width(img):
    """Get width of input image (path / PIL / numpy / tensor)."""
    # For numpy case
    if isinstance(img, np.ndarray):
        return img.shape[1]  # (H, W) or (C, H, W)

    # For cv2 path → load, return width
    if isinstance(img, (str, Path)):
        arr = cv2.imread(str(img), cv2.IMREAD_GRAYSCALE)
        if arr is None:
            raise ValueError(f"Failed to read image: {img}")
        return arr.shape[1]

    # PIL
    try:
        from PIL import Image
        if isinstance(img, Image.Image):
            return img.width
    except Exception:
        pass

    # Torch tensor
    try:
        import torch
        if isinstance(img, torch.Tensor):
            if img.dim() == 3:
                return img.size(2)  # (C, H, W)
            elif img.dim() == 2:
                return img.size(1)  # (H, W)
    except Exception:
        pass

    raise TypeError(f"Unsupported image type for getting width: {type(img)}")


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
        config: HipModelConfig = HipModelConfig(),
        device: Optional[str] = None,
    ):
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
            img_width = get_image_width(img2)
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
        image: Any,
        *,
        phase: str,
        seg_threshold: float = 0.5,
        seg_flip_if_left: bool = True,
        seg_only_if_hip: bool = True,
        ann_flip_if_left: bool = True,
        ann_only_if_hip: bool = True,
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
        output: Dict[str, Any] = {}

        # 1) Classify
        laterality, probability = self.classify(image, human_readable=True, return_probs=True)
        output["laterality_name"] = laterality
        output["laterality_probs"] = probability
        output["phase"] = self.phase

        # 2) Segment
        seg_mask = self.segment(
            image,
            phase=phase,
            threshold=seg_threshold,
            flip_if_left=seg_flip_if_left,
            only_if_hip=seg_only_if_hip,
        )
        output["segmentation"] = seg_mask

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

        output["success"] = True if (seg_mask is not None and annot is not None) else False

        predictions = HipModelPrediction(
            laterality_name=output["laterality_name"],
            laterality_probs=output["laterality_probs"],
            phase=output["phase"],
            segmentation=output["segmentation"],
            annotation_points=output["annotation_points"],
            annotation_vectors=output["annotation_vectors"],
            success=output["success"],
        )
        
        return output
    
    
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