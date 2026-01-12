"""
Inference UI with deterministic transforms, resizable square crop with handles,
per-degree rotation, prediction & GT contour overlays, keyboard shortcuts, and saving.

Place next to your `segmentation_prediction_v1.py` which must define:
- load_trained_model(model_path_or_None) -> model (callable) or None
- IMAGE_SIZE constant (width, height) used by your model

Dependencies:
pip install pillow numpy opencv-python torch

Run:
python segmentation_ui.py
"""

import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageOps
import numpy as np
import cv2
import torch 
from segment import UNet, ConvBlock, AttentionGate
from classify import ClassificationModel
from annotate import AnnotationModel

# Ground-truth label mapping and default keys used to find masks in per-image NPZs.
# These may be updated from a model checkpoint (see `load_trained_model`).
LABELS = {
    "_femur": "femur",
    "pelvis_mesh_hemi_": "pelvis",
    "pelvis_mesh_ramus_": "ramus",
    "_head": "head",
    "_cup": "cup",
    "_liner": "liner",
    "_stem": "stem",
}
# patterns used to locate masks inside `transformed_masks.npz` files (substring match, case-insensitive)
GT_KEYS = ["_femur", "pelvis_mesh_hemi_"]


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


def load_trained_model(weights_path=None, device=torch.device("cuda" if torch.cuda.is_available() else "cpu")):
    """Load and cache a UNet segmentation model. If weights_path is None, looks for 'best_model.pth' in a default folder.
    Returns the model or None on failure."""
    

    if weights_path is None:
        # Reasonable default: look for 'best_model.pth' in current working folder or segmentation folders
        candidate = os.path.join(r"models", "ref_seg_model.pth")
        if os.path.exists(candidate):
            weights_path = candidate

    if not weights_path or not os.path.exists(weights_path):
        print(f"Model weights not found at: {weights_path}")
        return None

    try:
        # model = torch.load(weights_path,  weights_only=False, map_location=device)
        
        # model = UNet(in_channels=1, out_channels=1).to(device)
        # model.load_state_dict(torch.load(weights_path, map_location=device))

        checkpoint = torch.load(str(weights_path), map_location=device)
        model = UNet(
            in_channels=checkpoint.get("in_channels", 1),
            out_channels=checkpoint.get("out_channels", 1)
        ).to(device)

        # Update global GT_KEYS and LABELS if checkpoint provides them
        global GT_KEYS, LABELS
        GT_KEYS = checkpoint.get("keys", GT_KEYS)

        # optional: allow checkpoints to ship a mapping of labels
        ck_labels = checkpoint.get("labels", None)
        if isinstance(ck_labels, dict):
            # merge/override defaults
            LABELS.update(ck_labels)

        model.load_state_dict(checkpoint["model_state_dict"])
        
    except Exception as e:
        print(f"Failed to load model weights: {e}")
        return None

    model.eval()
    print(f"Model loaded from: {weights_path}")
    return model


def load_classification_model(weights_path=None):
    """Load and cache a classification model for hip laterality. If weights_path is None, looks for default.
    Returns the model or None on failure."""
    
    if weights_path is None:
        # Reasonable default: look for 'best_classification.pth' in a default folder
        candidate = os.path.join(r"models", "later_class_model.pth")
        if os.path.exists(candidate):
            weights_path = candidate
    
    if not weights_path or not os.path.exists(weights_path):
        print(f"Classification model weights not found at: {weights_path}")
        return None
    
    try:
        classifier = ClassificationModel(model_path=weights_path)
        return classifier
    except Exception as e:
        print(f"Failed to load classification model: {e}")
        return None


def load_landmark_model(weights_path=None, device=None):
    """Load and cache a landmark regression model. If weights_path is None, looks for default.
    Returns the model or None on failure."""
    
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    if weights_path is None:
        # Reasonable default: look for 'best_landmark.pth' or 'ref_lm_model.pth' in a default folder
        candidates = [
            os.path.join(r"models", "ref_lm_model.pth"),
        ]
        for candidate in candidates:
            if os.path.exists(candidate):
                weights_path = candidate
                break
    
    if not weights_path or not os.path.exists(weights_path):
        print(f"Landmark model weights not found at: {weights_path}")
        return None
    
    try:
        landmark_model = AnnotationModel(weights_path, device=device)
        return landmark_model
    except Exception as e:
        print(f"Failed to load landmark model: {e}")
        return None

# Config
SUPPORTED_EXT = (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff")
DEFAULT_THRESHOLD = 0.5
DEBOUNCE_MS = 150  # milliseconds to wait after slider/drag before auto-run
HANDLE_SIZE = 10    # corner handle radius/half-size in display coordinates
CONTOUR_THICKNESS = 2
IMAGE_SIZE = (256, 256)

# Utility functions
def list_images_recursively(path):
    if os.path.isfile(path):
        return [path] if path.lower().endswith(SUPPORTED_EXT) else []
    out = []
    for root, _, files in os.walk(path):
        for f in sorted(files):
            if f.lower().endswith(SUPPORTED_EXT):
                out.append(os.path.join(root, f))
    return out

def pil_to_bgr_np(pil_img):
    arr = np.asarray(pil_img.convert("RGB"))
    # convert to BGR for opencv convenience
    return arr[:, :, ::-1].copy()

def bgr_np_to_pil(bgr):
    rgb = bgr[:, :, ::-1]
    return Image.fromarray(rgb)

def find_contours_binary(bin_mask):
    # expects mask uint8 with 0/255 values
    # Use RETR_TREE to get both outer and inner contours (for masks with holes)
    cnts, _ = cv2.findContours(bin_mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return cnts

def draw_contours_on_image(bgr_img, contours, color_bgr, thickness=2, alpha=1.0):
    # draw contours on a copy using blending with alpha
    overlay = bgr_img.copy()
    cv2.drawContours(overlay, contours, -1, color_bgr, thickness=thickness)
    if alpha < 1.0:
        blended = cv2.addWeighted(overlay, alpha, bgr_img, 1 - alpha, 0)
        return blended
    return overlay

def _match_key(keys: list, pattern: str, prefix: str) -> str:
    """
    Match a key from the list based on pattern and prefix.
    Matching rules:
     - if pattern starts with '_' -> expected = prefix + pattern
     - elif pattern ends with '_' -> expected = pattern + prefix
     - else expected = pattern
     - Try case-insensitive exact match first, then substring match.
    Returns matched key or None.
    """
    pat = pattern.lower()
    if pat.startswith("_"):
        expected = (prefix + pat).lower()
    elif pat.endswith("_"):
        expected = (pat + prefix).lower()
    else:
        expected = pat

    # exact match case-insensitive
    for k in keys:
        if k.lower() == expected:
            return k
    # fallback substring match
    for k in keys:
        if expected in k.lower() or pat in k.lower():
            return k
    return None

# Transform helpers (deterministic pipeline)
def apply_circular_border_to_image(pil_img):
    """
    Apply a circular border mask to a square PIL image.
    Creates a circle inscribed in the square (touching all edges).
    Everything outside the circle (but inside the square) is set to black (0).
    
    pil_img: PIL Image (should be square)
    Returns: PIL Image with circular mask applied
    """
    # Convert to numpy array
    arr = np.asarray(pil_img).astype(np.float32)
    h, w = arr.shape[:2]
    
    # Create circular mask: circle centered at (w/2, h/2) with radius = min(w,h)/2
    center = (w / 2, h / 2)
    # Inset the radius slightly so the black masked area doesn't lie exactly on the image edge.
    # This prevents the masked black border from being visually lost when it touches canvas edges.
    inset = 1.0
    radius = max(0.0, min(w, h) / 2 - inset)
    
    # Create coordinate grids
    yy, xx = np.ogrid[:h, :w]
    # Calculate distance from center for each pixel
    dist_from_center = np.sqrt((xx - center[0])**2 + (yy - center[1])**2)
    # Create mask: 1 inside circle, 0 outside
    mask = (dist_from_center <= radius).astype(np.float32)
    
    # Apply mask: multiply array by mask, set outside to 0
    if arr.ndim == 2:
        # Grayscale
        arr = arr * mask
    else:
        # Color/multi-channel
        arr = arr * mask[..., np.newaxis]
    
    # Convert back to PIL
    arr_uint8 = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr_uint8)

def apply_transforms_to_image(raw_pil, angle_deg, flip_horiz, brightness=1.0, contrast=1.0, smoothness=0.0, invert_colors=False):
    """
    Apply rotation (expand=True), horizontal flip, brightness, contrast, and smoothness (blur).
    Returns transformed PIL image.
    """
    if angle_deg % 360 != 0:
        transformed = raw_pil.rotate(angle_deg, expand=True, fillcolor=0)
    else:
        transformed = raw_pil.copy()
    if flip_horiz:
        transformed = ImageOps.mirror(transformed)

    # Apply color inversion
    if invert_colors:
        transformed = ImageOps.invert(transformed)
    
    # Apply brightness adjustment
    if abs(brightness - 1.0) > 0.01:
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Brightness(transformed)
        transformed = enhancer.enhance(brightness)
    
    # Apply contrast adjustment
    if abs(contrast - 1.0) > 0.01:
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(transformed)
        transformed = enhancer.enhance(contrast)
    
    # Apply smoothness (Gaussian blur)
    if smoothness > 0.01:
        from PIL import ImageFilter
        transformed = transformed.filter(ImageFilter.GaussianBlur(radius=smoothness))

    return transformed

def apply_transforms_to_mask(raw_mask_np, angle_deg, flip_horiz):
    """
    raw_mask_np: single-channel numpy array (uint8 or float), shape HxW, with raw-image alignment.
    Returns mask transformed exactly like apply_transforms_to_image (values preserved).
    Use NEAREST interpolation to preserve labels.
    """
    # convert to PIL (mode 'L')
    pil_mask = Image.fromarray((raw_mask_np * 255.0).astype(np.uint8)) if raw_mask_np.max() <= 1.0 else Image.fromarray(raw_mask_np.astype(np.uint8))
    if angle_deg % 360 != 0:
        pil_mask = pil_mask.rotate(angle_deg, expand=True, fillcolor=0)
    if flip_horiz:
        pil_mask = ImageOps.mirror(pil_mask)
    arr = np.asarray(pil_mask).astype(np.uint8)
    return arr

def inverse_transform_mask_on_canvas(pred_mask_crop_bin, transformed_image_size, crop_xywh, angle_deg, flip_horiz, raw_image_size):
    """
    pred_mask_crop_bin: numpy uint8 mask (0/255) of size (crop_size, crop_size)
    transformed_image_size: (W,H) of the transformed image (the one prediction was placed into)
    crop_xywh: (x,y,w,h) top-left and size in transformed image coordinates where crop sits
    angle_deg, flip_horiz: transforms that were applied to raw->transformed
    raw_image_size: (W_orig, H_orig) original raw image size

    Return: numpy uint8 mask aligned to raw image size (W_orig,H_orig) with 0/255 values.
    """

    # 1. Create blank mask in transformed-image space
    tw, th = transformed_image_size
    full_trans_mask = np.zeros((th, tw), dtype=np.uint8)
    x, y, w, h = crop_xywh
    # predicted crop may be different sized; assume pred_mask_crop_bin is square and size == w==h
    # ensure shape fits
    ch, cw = pred_mask_crop_bin.shape[:2]
    # if sizes differ, resize pred mask to fit crop
    if (cw, ch) != (w, h):
        resized = cv2.resize(pred_mask_crop_bin, (w, h), interpolation=cv2.INTER_NEAREST)
    else:
        resized = pred_mask_crop_bin
    full_trans_mask[y:y+h, x:x+w] = resized

    # 2. Inverse transforms: flip then rotate by -angle
    pil_mask_trans = Image.fromarray(full_trans_mask)
    if flip_horiz:
        pil_mask_trans = ImageOps.mirror(pil_mask_trans)  # inverse of mirror is mirror itself
    if angle_deg % 360 != 0:
        # rotate back by -angle; use expand=True to ensure content returns to original bounding box
        pil_mask_raw_candidate = pil_mask_trans.rotate(-angle_deg, expand=True, fillcolor=0)
    else:
        pil_mask_raw_candidate = pil_mask_trans

    # 3. After inverse rotation, the resulting canvas may be larger than original raw image; we need to center-crop
    cand = pil_mask_raw_candidate
    cand_w, cand_h = cand.size
    raw_w, raw_h = raw_image_size

    # center crop to raw size
    if cand_w >= raw_w and cand_h >= raw_h:
        left = (cand_w - raw_w) // 2
        top = (cand_h - raw_h) // 2
        cropped = cand.crop((left, top, left + raw_w, top + raw_h))
    else:
        # If candidate is smaller, paste into a black canvas centered
        base = Image.new("L", (raw_w, raw_h), 0)
        left = (raw_w - cand_w) // 2
        top = (raw_h - cand_h) // 2
        base.paste(cand, (left, top))
        cropped = base

    mask_raw_np = np.asarray(cropped).astype(np.uint8)
    # Return 0/255 mask
    return mask_raw_np

def apply_transforms_to_landmark_point(raw_image_size, landmark_point, angle_deg, flip_horiz):
    """
    Transform a landmark point by rotation and horizontal flip, matching apply_transforms_to_image.
    
    raw_image_size: (W, H) of the raw image where landmark is defined
    landmark_point: (x, y) coordinates in raw image space
    angle_deg: rotation in degrees
    flip_horiz: whether to apply horizontal flip
    
    Returns: (x_trans, y_trans) transformed landmark coordinates in the transformed image space.
    """
    # Create a dummy image to track how coordinates transform
    dummy_pil = Image.new("RGB", raw_image_size, color="white")
    raw_w, raw_h = raw_image_size
    px, py = landmark_point
    
    # Track bounding box to find offset after rotation
    # Create image with marked point
    dummy_arr = np.zeros((raw_h, raw_w), dtype=np.uint8)
    px_int, py_int = int(round(px)), int(round(py))
    if 0 <= px_int < raw_w and 0 <= py_int < raw_h:
        dummy_arr[py_int, px_int] = 255
    
    dummy_pil = Image.fromarray(dummy_arr, mode="L")
    
    # Apply transforms in same order as apply_transforms_to_image
    if angle_deg % 360 != 0:
        dummy_pil = dummy_pil.rotate(angle_deg, expand=True, fillcolor=0)
    if flip_horiz:
        dummy_pil = ImageOps.mirror(dummy_pil)
    
    # Find where the marked point moved to
    dummy_arr_trans = np.asarray(dummy_pil)
    points = np.where(dummy_arr_trans == 255)
    if len(points[0]) > 0:
        # Get center of marked region
        py_trans = float(np.mean(points[0]))
        px_trans = float(np.mean(points[1]))
        return (px_trans, py_trans)
    else:
        # Point went outside bounds after rotation, return None or original
        return None

# Main UI class
class SegmentationUI:
    def __init__(self, root):
        self.root = root
        root.title("Inference UI for Hip Segmentation, Landmarking, and Classification")

        # model & state
        self.model = None
        self.model_path = ""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # classification model
        self.classifier = None
        self.classifier_path = ""
        self.last_classification_result = None  # Store (class_name, percentage)

        # image state
        self.image_list = []
        self.current_index = -1
        self.current_path = None
        self.raw_pil = None              # raw grayscale PIL
        self.trans_pil = None            # transformed (rotated+flipped) PIL to display
        self.trans_size = (0, 0)         # width, height
        self.angle = 0                   # degrees (-180..180)
        self.flip_h = False
        self.invert_colors = False
        self.brightness = 1.0
        self.contrast = 1.0
        self.smoothness = 0.0
        self.threshold = DEFAULT_THRESHOLD

        # crop: stored in transformed-image coordinates
        # crop = [x, y, size] integers
        self.crop = None

        # mouse state for dragging/resizing
        self.dragging = False
        self.drag_type = None  # "move" or "handle-0..3"
        self.drag_start = (0, 0)
        self.crop_start = None

        # prediction / GT overlay state
        self.last_pred_probs = None      # float32 numpy in crop-size resolution (square)
        self.last_pred_bin = None        # uint8 0/255 binary crop mask
        self.pred_canvas_image = None    # cached PhotoImage for overlayed display
        self.show_prediction_var = tk.BooleanVar(value=False)
        self.show_gt_var = tk.BooleanVar(value=False)
        self.threshold_var = tk.DoubleVar(value=self.threshold)

        # Option to use classifier guidance: when enabled, classifier output will
        # guide whether to mirror inputs and whether to run predictions.
        # (Previously: 'Mirror If Left Hip (use classifier)')
        self.mirror_left_var = tk.BooleanVar(value=False)

        # Option to apply circular border: when enabled, a circular mask will be applied
        # to the crop area (inscribed circle centered in square crop, black outside)
        self.circular_border_var = tk.BooleanVar(value=False)

        # landmark state
        self.landmark_model = None
        self.landmark_path = ""
        self.last_landmarks_pred = None  # dict with 'points' and 'vectors' from prediction
        self.show_landmarks_var = tk.BooleanVar(value=False)
        self.show_landmarks_gt_var = tk.BooleanVar(value=False)

        # debounce
        self._debounce_after_id = None

        # hover state
        self.landmark_hover_items = []  # list of dicts: {x, y, name, kind}
        self._hover_tip = None
        self._hover_tip_label = None

        # build UI
        self.build_ui()

        # attempt to load default model using load_trained_model(None)
        self.attempt_default_model_load()

    def build_ui(self):
        # layout: left canvas, right controls
        main = ttk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(left, bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        # canvas bindings
        self.canvas.bind("<Button-1>", self.on_canvas_down)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_up)
        self.canvas.bind("<Configure>", lambda e: self.redraw())

        self.canvas.bind("<Motion>", self.on_canvas_motion)
        self.canvas.bind("<Leave>", self.on_canvas_leave)

        # right controls
        right = ttk.Frame(main, width=360)
        right.pack(side=tk.RIGHT, fill=tk.Y)

        # Classification Model Section
        clf_model_frame = ttk.LabelFrame(right, text="Classification Model (Laterality)")
        clf_model_frame.pack(fill=tk.X, padx=6, pady=6)
        clf_entry_frame = ttk.Frame(clf_model_frame)
        clf_entry_frame.pack(fill=tk.X, padx=6, pady=4)
        self.clf_model_path_var = tk.StringVar()
        ttk.Entry(clf_entry_frame, textvariable=self.clf_model_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ttk.Button(clf_entry_frame, text="Browse...", command=self.browse_classifier, width=10).pack(side=tk.LEFT, padx=2)
        
        # Model Section - Segmentation
        model_frame = ttk.LabelFrame(right, text="Segmentation Model")
        model_frame.pack(fill=tk.X, padx=6, pady=6)
        model_entry_frame = ttk.Frame(model_frame)
        model_entry_frame.pack(fill=tk.X, padx=6, pady=4)
        self.model_path_var = tk.StringVar()
        ttk.Entry(model_entry_frame, textvariable=self.model_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ttk.Button(model_entry_frame, text="Browse...", command=self.browse_model, width=10).pack(side=tk.LEFT, padx=2)

        # Landmark Model Section
        lm_model_frame = ttk.LabelFrame(right, text="Landmark Model")
        lm_model_frame.pack(fill=tk.X, padx=6, pady=6)
        lm_entry_frame = ttk.Frame(lm_model_frame)
        lm_entry_frame.pack(fill=tk.X, padx=6, pady=4)
        self.lm_model_path_var = tk.StringVar()
        ttk.Entry(lm_entry_frame, textvariable=self.lm_model_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ttk.Button(lm_entry_frame, text="Browse...", command=self.browse_landmark_model, width=10).pack(side=tk.LEFT, padx=2)

        # I/O
        io_frame = ttk.LabelFrame(right, text="Input / Navigation")
        io_frame.pack(fill=tk.X, padx=6, pady=6)
        self.input_path_var = tk.StringVar()
        input_entry_frame = ttk.Frame(io_frame)
        input_entry_frame.pack(fill=tk.X, padx=6, pady=4)
        ttk.Entry(input_entry_frame, textvariable=self.input_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ttk.Button(input_entry_frame, text="Image", command=self.choose_image, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(input_entry_frame, text="Folder", command=self.choose_folder, width=8).pack(side=tk.LEFT, padx=2)
        nav = ttk.Frame(io_frame)
        nav.pack(fill=tk.X, padx=6, pady=4)
        ttk.Button(nav, text="<< Prev", command=self.prev_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav, text="Next >>", command=self.next_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav, text="Save mask (Ctrl+S)", command=self.save_mask_dialog).pack(side=tk.RIGHT, padx=2)

        # Options
        opt = ttk.LabelFrame(right, text="Overlays")
        opt.pack(fill=tk.X, padx=6, pady=6)
        seg_frame = ttk.Frame(opt)
        seg_frame.pack(fill=tk.X, padx=6, pady=2)
        ttk.Checkbutton(seg_frame, text="Seg Pred", variable=self.show_prediction_var, command=self.on_toggle_prediction).pack(side=tk.LEFT, padx=2)
        ttk.Checkbutton(seg_frame, text="Seg GT", variable=self.show_gt_var, command=self.redraw).pack(side=tk.LEFT, padx=2)
        lm_frame = ttk.Frame(opt)
        lm_frame.pack(fill=tk.X, padx=6, pady=2)
        ttk.Checkbutton(lm_frame, text="LM Pred", variable=self.show_landmarks_var, command=self.on_toggle_landmarks).pack(side=tk.LEFT, padx=2)
        ttk.Checkbutton(lm_frame, text="LM GT", variable=self.show_landmarks_gt_var, command=self.redraw).pack(side=tk.LEFT, padx=2)
        # Checkboxes for classifier guidance and circular border
        guidance_frame = ttk.Frame(opt)
        guidance_frame.pack(fill=tk.X, padx=6, pady=(4,2))
        ttk.Checkbutton(guidance_frame, text="Use classifier to guide predictions", variable=self.mirror_left_var, command=self.on_toggle_mirror).pack(side=tk.LEFT, padx=2)
        ttk.Checkbutton(guidance_frame, text="Circular border", variable=self.circular_border_var, command=self.on_toggle_circular_border).pack(side=tk.LEFT, padx=2)

        # Transform controls
        trans_frame = ttk.LabelFrame(right, text="Transforms")
        trans_frame.pack(fill=tk.X, padx=6, pady=6)
        
        # flip and reset buttons
        flip_frame = ttk.Frame(trans_frame)
        flip_frame.pack(fill=tk.X, padx=6, pady=4)
        ttk.Button(flip_frame, text="Flip horizontally (F)", command=self.toggle_flip).pack(side=tk.LEFT, expand=True, padx=2)
        ttk.Button(flip_frame, text="Invert colors (I)", command=self.toggle_invert).pack(side=tk.LEFT, expand=True, padx=2)
        ttk.Button(flip_frame, text="Reset all transforms", command=self.reset_all_transforms).pack(side=tk.LEFT, expand=True, padx=2)

        # rotation slider 0..359
        ttk.Label(trans_frame, text="Rotation (degrees)").pack(anchor=tk.W, padx=6)
        # Rotation slider centered at 0 degrees: range -180..+180 so 0 is at the middle
        rotation_frame = ttk.Frame(trans_frame)
        rotation_frame.pack(fill=tk.X, padx=6, pady=2)
        self.rot_scale = tk.Scale(rotation_frame, from_=-180, to=180, orient=tk.HORIZONTAL, showvalue=True,
                      command=self.on_rotation_change, length=200, resolution=1)
        self.rot_scale.set(0)
        self.rot_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(rotation_frame, text="Reset", command=self.reset_rotation, width=8).pack(side=tk.LEFT, padx=4)

        # brightness slider
        ttk.Label(trans_frame, text="Brightness (0.0-2.0)").pack(anchor=tk.W, padx=6)
        brightness_frame = ttk.Frame(trans_frame)
        brightness_frame.pack(fill=tk.X, padx=6, pady=2)
        self.brightness_var = tk.DoubleVar(value=1.0)
        self.brightness_scale = tk.Scale(brightness_frame, from_=0.0, to=2.0, resolution=0.1, orient=tk.HORIZONTAL,
                                          variable=self.brightness_var, command=self.on_adjustment_change, length=200)
        self.brightness_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(brightness_frame, text="Reset", command=self.reset_brightness, width=8).pack(side=tk.LEFT, padx=4)

        # contrast slider
        ttk.Label(trans_frame, text="Contrast (0.0-2.0)").pack(anchor=tk.W, padx=6, pady=(6, 0))
        contrast_frame = ttk.Frame(trans_frame)
        contrast_frame.pack(fill=tk.X, padx=6, pady=2)
        self.contrast_var = tk.DoubleVar(value=1.0)
        self.contrast_scale = tk.Scale(contrast_frame, from_=0.0, to=2.0, resolution=0.1, orient=tk.HORIZONTAL,
                                        variable=self.contrast_var, command=self.on_adjustment_change, length=200)
        self.contrast_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(contrast_frame, text="Reset", command=self.reset_contrast, width=8).pack(side=tk.LEFT, padx=4)

        # smoothness (blur) slider
        ttk.Label(trans_frame, text="Smoothness (0.0-5.0)").pack(anchor=tk.W, padx=6, pady=(6, 0))
        smoothness_frame = ttk.Frame(trans_frame)
        smoothness_frame.pack(fill=tk.X, padx=6, pady=2)
        self.smoothness_var = tk.DoubleVar(value=0.0)
        self.smoothness_scale = tk.Scale(smoothness_frame, from_=0.0, to=5.0, resolution=0.1, orient=tk.HORIZONTAL,
                                          variable=self.smoothness_var, command=self.on_adjustment_change, length=200)
        self.smoothness_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(smoothness_frame, text="Reset", command=self.reset_smoothness, width=8).pack(side=tk.LEFT, padx=4)

        # threshold slider
        thr_frame = ttk.LabelFrame(right, text="Mask threshold")
        thr_frame.pack(fill=tk.X, padx=6, pady=6)
        thr_inner = ttk.Frame(thr_frame)
        thr_inner.pack(fill=tk.X, padx=6, pady=4)
        self.thr_scale = tk.Scale(thr_inner, from_=0.0, to=1.0, resolution=0.01, orient=tk.HORIZONTAL,
                                  variable=self.threshold_var, command=self.on_threshold_change, length=200)
        self.thr_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(thr_inner, text="Reset", command=self.reset_threshold, width=8).pack(side=tk.LEFT, padx=4)

        # status
        status = ttk.LabelFrame(right, text="Status")
        status.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.status_box = tk.Text(status, height=10, wrap=tk.WORD)
        self.status_box.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.log("Ready.")

        # Keyboard shortcuts
        self.root.bind("<Left>", lambda e: self.prev_image())
        self.root.bind("<Right>", lambda e: self.next_image())
        self.root.bind("<r>", lambda e: self.reset_rotation())
        self.root.bind("<R>", lambda e: self.reset_rotation())
        self.root.bind("<f>", lambda e: self.toggle_flip())
        self.root.bind("<F>", lambda e: self.toggle_flip())
        self.root.bind("<i>", lambda e: self.toggle_invert())
        self.root.bind("<I>", lambda e: self.toggle_invert())
        self.root.bind("<Escape>", lambda e: self.cancel_drag())
        self.root.bind_all("<Control-s>", lambda e: self.save_mask_dialog())

    def log(self, *args):
        txt = " ".join(str(a) for a in args) + "\n"
        self.status_box.insert(tk.END, txt)
        self.status_box.see(tk.END)

    def attempt_default_model_load(self):
        # Load segmentation model
        try:
            mdl = load_trained_model() # r"E:\tmp\split_4patients_random\segmentation\best_model_full.pth"
            if mdl is not None:
                self.model = mdl
                # try to infer device
                params = list(self.model.parameters()) if hasattr(self.model, "parameters") else []
                if params:
                    self.device = next(self.model.parameters()).device
                self.model_path_var.set("<default loaded>")
                self.log("Default segmentation model loaded.")
            else:
                self.log("No default segmentation model found.")
        except Exception as e:
            self.log("Default segmentation model load error:", e)
        
        # Load classification model
        try:
            clf = load_classification_model()
            if clf is not None:
                self.classifier = clf
                self.clf_model_path_var.set("<default loaded>")
                self.log("Default classification model loaded.")
            else:
                self.log("No default classification model found.")
        except Exception as e:
            self.log("Default classification model load error:", e)

        # Load landmark model
        try:
            lm = load_landmark_model(device=self.device)
            if lm is not None:
                self.landmark_model = lm
                self.lm_model_path_var.set("<default loaded>")
                self.log("Default landmark model loaded.")
            else:
                self.log("No default landmark model found.")
        except Exception as e:
            self.log("Default landmark model load error:", e)

    def browse_model(self):
        path = filedialog.askopenfilename(title="Select segmentation model file", filetypes=[("PyTorch", "*.pt *.pth"), ("All files", "*.*")])
        if not path:
            return
        try:
            mdl = load_trained_model(path)
            if mdl is None:
                messagebox.showwarning("Model", "Failed to load segmentation model.")
                self.model_path_var.set("")
                return
            self.model = mdl
            params = list(self.model.parameters()) if hasattr(self.model, "parameters") else []
            if params:
                self.device = next(self.model.parameters()).device
            self.model_path_var.set(path)
            self.log("Segmentation model loaded:", path)
            # Auto-run prediction if checkbox is enabled
            if self.show_prediction_var.get():
                self._debounced_run()
        except Exception as e:
            messagebox.showerror("Model load", str(e))
            self.log("Model load error:", e)
    
    def browse_classifier(self):
        path = filedialog.askopenfilename(title="Select classification model file", filetypes=[("PyTorch", "*.pt *.pth"), ("All files", "*.*")])
        if not path:
            return
        try:
            clf = load_classification_model(path)
            if clf is None:
                messagebox.showwarning("Classification Model", "Failed to load classification model.")
                self.clf_model_path_var.set("")
                return
            self.classifier = clf
            self.clf_model_path_var.set(path)
            self.log("Classification model loaded:", path)
            # Run classification if we have an image
            if self.trans_pil is not None:
                self._run_classification_on_current()
        except Exception as e:
            messagebox.showerror("Classification model load", str(e))
            self.log("Classification model load error:", e)

    def browse_landmark_model(self):
        path = filedialog.askopenfilename(title="Select landmark model file", filetypes=[("PyTorch", "*.pt *.pth"), ("All files", "*.*")])
        if not path:
            return
        try:
            lm = load_landmark_model(path, device=self.device)
            if lm is None:
                messagebox.showwarning("Landmark Model", "Failed to load landmark model.")
                self.lm_model_path_var.set("")
                return
            self.landmark_model = lm
            self.lm_model_path_var.set(path)
            self.log("Landmark model loaded:", path)
            # Run landmark prediction if we have an image
            if self.trans_pil is not None and self.show_landmarks_var.get():
                self._run_landmark_prediction_on_current()
        except Exception as e:
            messagebox.showerror("Landmark model load", str(e))
            self.log("Landmark model load error:", e)

    # IO and navigation
    def choose_folder(self):
        p = filedialog.askdirectory(title="Choose folder", initialdir=os.path.join(os.getcwd(), "Testing"))
        if not p:
            return
        self.input_path_var.set(p)
        self.image_list = list_images_recursively(p)
        if not self.image_list:
            messagebox.showinfo("No images", "No supported images found.")
            self.log("No images in", p)
            return
        self.current_index = 0
        self.load_current()
        self.log(f"Loaded {len(self.image_list)} images from {p}")

    def choose_image(self):
        p = filedialog.askopenfilename(title="Choose image", filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff")])
        if not p:
            return
        self.input_path_var.set(p)
        self.image_list = [p]
        self.current_index = 0
        self.load_current()

    def prev_image(self):
        if not self.image_list:
            return
        self.current_index = (self.current_index - 1) % len(self.image_list)
        self.load_current()

    def next_image(self):
        if not self.image_list:
            return
        self.current_index = (self.current_index + 1) % len(self.image_list)
        self.load_current()

    def load_current(self):
        if self.current_index < 0 or self.current_index >= len(self.image_list):
            return
        path = self.image_list[self.current_index]
        self.current_path = path
        self.input_path_var.set(path)
        try:
            pil = Image.open(path).convert("L")  # load grayscale
        except Exception as e:
            self.log("Failed to open image:", e)
            return
        self.raw_pil = pil
        # reset transforms
        self.angle = 0
        self.flip_h = False
        self.invert_colors = False
        self.rot_scale.set(0)
        # apply transforms to get display image
        self.trans_pil = apply_transforms_to_image(self.raw_pil, self.angle, self.flip_h, self.brightness, self.contrast, self.smoothness, self.invert_colors)
        self.trans_size = self.trans_pil.size
        # set initial crop as centered square occupying min dimension
        tw, th = self.trans_size
        side = min(tw, th)
        x = (tw - side) // 2
        y = (th - side) // 2
        self.crop = [x, y, side]
        self.last_pred_probs = None
        self.last_pred_bin = None
        self.last_classification_result = None
        self.last_landmarks_pred = None
        self.redraw()
        self.log("Loaded", path)
        if self.show_prediction_var.get():
            self._debounced_run()
        # Run classification on full transformed image
        if self.classifier is not None:
            self._run_classification_on_current()
        # Run landmark prediction on full transformed image
        if self.landmark_model is not None and self.show_landmarks_var.get():
            self._run_landmark_prediction_on_current()

    # Canvas coordinate mapping:
    # We display transformed image resized to fit canvas while preserving aspect.
    # We must convert between display coords (image pixels) and canvas pixels for drawing handles.
    def get_display_mapping(self):
        """Return (scale, xoff, yoff, disp_w, disp_h) mapping display-image coords to canvas coords:
           canvas_x = xoff + x * scale
        """
        if self.trans_pil is None:
            return 1.0, 0, 0, 0, 0
        cw = max(1, self.canvas.winfo_width())
        ch = max(1, self.canvas.winfo_height())
        iw, ih = self.trans_pil.size
        scale = min(cw / iw, ch / ih)
        disp_w = int(iw * scale)
        disp_h = int(ih * scale)
        xoff = (cw - disp_w) // 2
        yoff = (ch - disp_h) // 2
        return scale, xoff, yoff, disp_w, disp_h

    def display_to_canvas(self, dx, dy):
        s, xoff, yoff, _, _ = self.get_display_mapping()
        return int(xoff + dx * s), int(yoff + dy * s)

    def canvas_to_display(self, cx, cy):
        s, xoff, yoff, _, _ = self.get_display_mapping()
        dx = (cx - xoff) / s
        dy = (cy - yoff) / s
        return int(dx), int(dy)

    # Drawing
    def redraw(self):
        self.landmark_hover_items.clear()

        self.canvas.delete("all")
        if self.trans_pil is None:
            return
        
        # Update window title with classification result if available
        if self.last_classification_result:
            class_name, percentage = self.last_classification_result
            title = f"Inference UI - {class_name} ({percentage})"
        else:
            title = "Inference UI for Hip Segmentation, Landmarking, and Classification"
        self.root.title(title)
        
        # Resize transformed image to fit and draw
        s, xoff, yoff, disp_w, disp_h = self.get_display_mapping()
        
        # Set canvas scrollregion to accommodate the entire displayed image
        # This ensures the image is not clipped at canvas edges
        self.canvas.config(scrollregion=(xoff, yoff, xoff + disp_w, yoff + disp_h))
        
        resized = self.trans_pil.resize((disp_w, disp_h), Image.BILINEAR)
        
        # Apply circular mask to base image if enabled (before overlays)
        if self.circular_border_var.get() and self.crop is not None:
            resized = self._apply_circular_mask_to_pil(resized, (s, disp_w, disp_h))
        
        self._tk_img = ImageTk.PhotoImage(resized.convert("RGB"))
        self.canvas.create_image(xoff, yoff, anchor="nw", image=self._tk_img, tags=("IMG",))
        # draw GT and prediction contours on top if available
        # We'll create an overlay image in display-image coords for accuracy, then place onto canvas.
        overlay_bgr = pil_to_bgr_np(resized)  # BGR numpy (now includes circular mask if enabled)
        # overlay GT (red contours)
        if self.show_gt_var.get():
            self._overlay_ground_truth_on_bgr(overlay_bgr, (s, xoff, yoff))
        # overlay prediction (green contours)
        if self.last_pred_bin is not None and self.show_prediction_var.get():
            self._overlay_prediction_on_bgr(overlay_bgr, (s, xoff, yoff))
        # overlay landmark GT (red)
        if self.show_landmarks_gt_var.get():
            self._overlay_landmarks_gt_on_bgr(overlay_bgr, (s, xoff, yoff))
        # overlay landmark predictions (green)
        if self.last_landmarks_pred is not None and self.show_landmarks_var.get():
            self._overlay_landmarks_pred_on_bgr(overlay_bgr, (s, xoff, yoff))

        # convert overlay_bgr back to PIL and put on canvas as image layer
        overlay_pil = bgr_np_to_pil(overlay_bgr)
        self._tk_overlay = ImageTk.PhotoImage(overlay_pil)
        self.canvas.create_image(xoff, yoff, anchor="nw", image=self._tk_overlay)

        # draw crop rectangle and handles (in canvas coords)
        if self.crop is not None:
            x, y, side = self.crop
            x1, y1 = self.display_to_canvas(x, y)
            x2, y2 = self.display_to_canvas(x + side, y + side)
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="yellow", width=2, tags=("CROP",))
            # handles at corners: top-left, top-right, bottom-right, bottom-left
            corners = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
            for i, (hx, hy) in enumerate(corners):
                self.canvas.create_rectangle(hx - HANDLE_SIZE, hy - HANDLE_SIZE, hx + HANDLE_SIZE, hy + HANDLE_SIZE,
                                             fill="yellow", outline="black", tags=(f"H{i}",))

    def _overlay_ground_truth_on_bgr(self, overlay_bgr, mapping):
        """
        overlay_bgr is BGR numpy corresponding to resized transformed image (display size).
        mapping = (scale, xoff, yoff), used to compute coordinates.
        We'll try to load transformed_masks.npz & image_config.json from image folder,
        apply transforms deterministically, resize them to transformed-image size and draw contours.
        Supports both femur-only and femur+pelvis models.
        """
        if not self.current_path:
            return
        folder = os.path.dirname(self.current_path)
        mask_npz = os.path.join(folder, "transformed_masks.npz")
        config_json = os.path.join(folder, "image_config.json")
        if not (os.path.exists(mask_npz) and os.path.exists(config_json)):
            # no GT available
            return
        try:
            data = np.load(mask_npz)
            # require config.json for side detection (mandatory)
            with open(config_json, "r") as f:
                cfg = json.load(f)
            prefix = "left" if cfg.get("left", False) else "right"

            s, xoff, yoff, disp_w, disp_h = self.get_display_mapping()

            # Use global GT_KEYS patterns to find matching mask entries in the NPZ
            global GT_KEYS, LABELS
            keys = [k for k in getattr(data, 'files', list(data.keys()))]

            # For each pattern in GT_KEYS require exact side-key (no substring fallback)
            for pattern in GT_KEYS:
                found_key = _match_key(keys, pattern, prefix)
                if found_key is None:
                    # missing expected GT key for this side
                    self.log(f"GT key not found for pattern '{pattern}' with side '{prefix}'")
                    continue
                try:
                    mask = data[found_key].astype(np.float32, copy=True)
                    if mask.max() > 1.0:
                        mask = mask / 255.0
                    mask_u8 = (mask * 255.0).astype(np.uint8)
                    # Apply same transforms (rotation + flip)
                    mask_trans = apply_transforms_to_mask(mask_u8, self.angle, self.flip_h)
                    mask_resized = cv2.resize(mask_trans, (disp_w, disp_h), interpolation=cv2.INTER_NEAREST)
                    mask_bin = (mask_resized >= 128).astype(np.uint8) * 255
                    cnts = find_contours_binary(mask_bin)
                    if not cnts:
                        continue
                    # choose color (red) for GT, could be extended per-label
                    color = (0, 0, 255)
                    cv2.drawContours(overlay_bgr, cnts, -1, color, thickness=CONTOUR_THICKNESS)
                except Exception as ex:
                    self.log("GT overlay mask error for key", found_key, ex)
                    continue
        except Exception as e:
            self.log("GT overlay error:", e)

    def _overlay_prediction_on_bgr(self, overlay_bgr, mapping):
        """
        overlay_bgr is BGR numpy corresponding to resized transformed image.
        mapping: (scale, xoff, yoff)
        Use last_pred_bin (which is a square crop binary 0/255, in crop-size resolution).
        Supports both single-channel (femur) and multi-channel (femur+pelvis) predictions.
        We need to place it into overlay_bgr at crop location scaled to display size.
        """
        if self.last_pred_bin is None:
            return
        s, xoff, yoff, disp_w, disp_h = self.get_display_mapping()
        x, y, side = self.crop
        # crop coords in transformed image, scaled
        # Compute scaled crop rectangle in display/resized coords:
        cx1 = int(round(x * s))
        cy1 = int(round(y * s))
        cW = int(round(side * s))
        cH = cW
        
        if self.last_pred_bin.ndim == 2:
            # Single-channel prediction (femur only): shape (side, side)
            pred_resized = cv2.resize(self.last_pred_bin, (cW, cH), interpolation=cv2.INTER_NEAREST)
            cnts = find_contours_binary(pred_resized)
            if not cnts:
                return
            # Offset contours by (cx1, cy1)
            shifted = []
            for c in cnts:
                c2 = c.copy()
                c2[:, 0, 0] += cx1
                c2[:, 0, 1] += cy1
                shifted.append(c2)
            # draw green contours for femur predictions
            cv2.drawContours(overlay_bgr, shifted, -1, (0, 255, 0), thickness=CONTOUR_THICKNESS)
        else:
            # Multi-channel prediction: shape (C, side, side)
            # All predictions drawn in green
            colors = [(0, 255, 0), (255, 0 , 0), (128, 128, 0)]  # Green for all predictions (femur and pelvis)
            for c in range(min(self.last_pred_bin.shape[0], len(colors))):
                pred_bin_c = self.last_pred_bin[c]  # shape (side, side)
                pred_resized = cv2.resize(pred_bin_c, (cW, cH), interpolation=cv2.INTER_NEAREST)
                cnts = find_contours_binary(pred_resized)
                if not cnts:
                    continue
                # Offset contours by (cx1, cy1)
                shifted = []
                for cnt in cnts:
                    cnt2 = cnt.copy()
                    cnt2[:, 0, 0] += cx1
                    cnt2[:, 0, 1] += cy1
                    shifted.append(cnt2)
                # Draw contours in green for predictions (includes inner contours)
                cv2.drawContours(overlay_bgr, shifted, -1, colors[c], thickness=CONTOUR_THICKNESS)

    def _overlay_landmarks_gt_on_bgr(self, overlay_bgr, mapping):
        """
        Overlay ground truth landmarks on the image.
        Only plots landmarks that the model is trained to predict (from model metadata).
        Loads transformed_landmarks.npz from the image directory.
        Applies rotation and flip transforms to landmark points to match image transforms.
        Draws landmarks (red dots).
        """
        if not self.current_path or self.landmark_model is None:
            return
        folder = os.path.dirname(self.current_path)
        landmarks_npz = os.path.join(folder, "transformed_landmarks.npz")
        config_json = os.path.join(folder, "image_config.json")
        
        if not os.path.exists(landmarks_npz):
            return
        
        try:
            data = np.load(landmarks_npz, allow_pickle=True)
            keys = list(getattr(data, 'files', list(data.keys())))
            
            # Get side (left/right) from config
            prefix = ""
            if os.path.exists(config_json):
                try:
                    with open(config_json, "r") as f:
                        cfg = json.load(f)
                    prefix = "left" if cfg.get("left", False) else "right"
                except:
                    pass
            
            # Get landmarks the model is trained to predict
            model_landmarks = list(self.landmark_model.meta.get("landmarks", []))
            if not model_landmarks:
                self.log("No landmarks defined in landmark model metadata")
                return
            
            s, xoff, yoff, disp_w, disp_h = self.get_display_mapping()
            
            # Draw only the landmarks the model predicts (red dots)
            drawn_count = 0
            for lm_name in model_landmarks:
                # Find the key in NPZ that matches this landmark name with side prefix
                key = _match_key(keys, lm_name, prefix)
                if key is None:
                    continue
                
                try:
                    point = data[key]
                    if isinstance(point, np.ndarray) and point.size >= 2:
                        px, py = float(point[0]), float(point[1])
                        # Apply transforms (rotation and flip) to landmark point
                        transformed_pt = apply_transforms_to_landmark_point(self.raw_pil.size, (px, py), self.angle, self.flip_h)
                        if transformed_pt is None:
                            # Point went outside bounds after transformation
                            continue
                        px_trans, py_trans = transformed_pt
                        # Scale to display coordinates
                        dpx = int(round(px_trans * s))
                        dpy = int(round(py_trans * s))

                        # Draw red circle
                        cv2.circle(overlay_bgr, (dpx, dpy), radius=5, color=(0, 0, 255), thickness=-1)
                        cv2.circle(overlay_bgr, (dpx, dpy), radius=8, color=(0, 0, 0), thickness=1)
                        
                        _, xoff, yoff, _, _ = self.get_display_mapping()
                        self.landmark_hover_items.append({
                            "x": xoff + dpx,
                            "y": yoff + dpy,
                            "name": lm_name,
                            "kind": "GT"
                        })

                        drawn_count += 1
                except Exception as ex:
                    pass
            
            # self.log(f"GT Landmarks: Drew {drawn_count}/{len(model_landmarks)} landmarks that model predicts")
        
        except Exception as e:
            self.log("GT landmarks overlay error:", e)

    def _overlay_landmarks_pred_on_bgr(self, overlay_bgr, mapping):
        """
        Overlay predicted landmarks on the image.
        Uses last_landmarks_pred which contains 'points' and 'vectors' dicts.
        Predictions are in crop-space coordinates, so we need to offset them to transformed-image coords.
        Draws landmarks (green dots) and vectors (green arrows or lines).
        """
        if self.last_landmarks_pred is None or self.crop is None:
            return
        
        s, xoff, yoff, disp_w, disp_h = self.get_display_mapping()
        points = self.last_landmarks_pred.get('points', {})
        vectors = self.last_landmarks_pred.get('vectors', {})
        
        # Get crop position in transformed image space
        crop_x, crop_y, crop_side = self.crop
        
        # Get transformed image size for clipping
        tw, th = self.trans_size
        
        # Get axis representation
        axis_repr = self.landmark_model.meta.get("axis_repr", "anchor_dir")
        
        try:
            # Draw predicted landmark points (green)
            # Landmarks are in crop-space, so offset by crop position
            for pt_name, (px, py) in points.items():
                # Convert from crop-space to transformed-image space
                img_px = crop_x + px
                img_py = crop_y + py
                # Scale to display coordinates
                dpx = int(round(img_px * s))
                dpy = int(round(img_py * s))
                cv2.circle(overlay_bgr, (dpx, dpy), radius=5, color=(0, 255, 0), thickness=-1)
                cv2.circle(overlay_bgr, (dpx, dpy), radius=8, color=(0, 0, 0), thickness=1)

                _, xoff, yoff, _, _ = self.get_display_mapping()
                self.landmark_hover_items.append({
                    "x": xoff + dpx,
                    "y": yoff + dpy,
                    "name": pt_name,
                    "kind": "Pred"
                })
            
            # Draw predicted vectors (green arrows or lines)
            for (A_name, B_name), (anchor, end) in vectors.items():
                ax, ay = anchor
                bx, by = end
                # Convert from crop-space to transformed-image space
                img_ax = crop_x + ax
                img_ay = crop_y + ay
                img_bx = crop_x + bx
                img_by = crop_y + by
                
                if axis_repr in ["rho_theta", "rho_dir"]:
                    # For rho_theta or rho_dir, draw the full line clipped to image boundaries
                    direction_vec = (img_bx - img_ax, img_by - img_ay)
                    p1, p2 = _clip_line_to_image((img_ax, img_ay), direction_vec, tw, th)
                    if p1 and p2:
                        # Scale to display coordinates
                        dp1x = int(round(p1[0] * s))
                        dp1y = int(round(p1[1] * s))
                        dp2x = int(round(p2[0] * s))
                        dp2y = int(round(p2[1] * s))
                        cv2.line(overlay_bgr, (dp1x, dp1y), (dp2x, dp2y), color=(0, 255, 0), thickness=2)
                else:
                    # For anchor_dir or other anchored vectors, draw an arrow from start to end
                    # Scale to display coordinates
                    dax = int(round(img_ax * s))
                    day = int(round(img_ay * s))
                    dbx = int(round(img_bx * s))
                    dby = int(round(img_by * s))
                    cv2.arrowedLine(overlay_bgr, (dax, day), (dbx, dby), color=(0, 255, 0), thickness=2, tipLength=0.1)
        
        except Exception as e:
            self.log("Predicted landmarks overlay error:", e)

    def _apply_circular_mask_to_pil(self, pil_img, mapping):
        """
        Apply a black circular mask to the crop area in a PIL image.
        Everything outside the inscribed circle (but inside the square crop) becomes black.
        Returns a new PIL image with the mask applied.
        mapping: (scale, disp_w, disp_h)
        """
        if self.crop is None:
            return pil_img
        
        s, disp_w, disp_h = mapping
        x, y, side = self.crop
        
        # Convert PIL to numpy
        img_arr = np.asarray(pil_img).astype(np.uint8)
        
        # Crop area in display coordinates (scaled)
        cx1 = int(round(x * s))
        cy1 = int(round(y * s))
        cW = int(side * s) - 1  # to avoid boundary issues that causes disappearing circle
        cH = cW 
        
        # Create circular mask for the crop region
        # Center of circle in crop coordinates
        center = (cW / 2, cH / 2)
        radius = cW / 2
        
        # Create coordinate grids for the crop area
        yy, xx = np.ogrid[:cH, :cW]
        dist_from_center = np.sqrt((xx - center[0])**2 + (yy - center[1])**2)
        circle_mask = (dist_from_center <= radius).astype(np.uint8)
        
        # Apply mask: keep circle area, black out the rest
        if cx1 + cW <= img_arr.shape[1] and cy1 + cH <= img_arr.shape[0]:
            if img_arr.ndim == 3:
                # Color image
                img_arr[cy1:cy1+cH, cx1:cx1+cW, 0] *= circle_mask  # B or R
                img_arr[cy1:cy1+cH, cx1:cx1+cW, 1] *= circle_mask  # G
                img_arr[cy1:cy1+cH, cx1:cx1+cW, 2] *= circle_mask  # R or B
            else:
                # Grayscale
                img_arr[cy1:cy1+cH, cx1:cx1+cW] *= circle_mask
        
        # Convert back to PIL
        return Image.fromarray(img_arr)

    def on_canvas_motion(self, event):
        if not self.landmark_hover_items:
            self._hide_hover_tip()
            return

        mx, my = event.x, event.y
        radius = 8  # hover tolerance in pixels

        for item in self.landmark_hover_items:
            dx = mx - item["x"]
            dy = my - item["y"]
            if dx * dx + dy * dy <= radius * radius:
                self._show_hover_tip(
                    event.x_root,
                    event.y_root,
                    f'{item["name"]} ({item["kind"]})'
                )
                return

        self._hide_hover_tip()

    def on_canvas_leave(self, event):
        self._hide_hover_tip()

    def _show_hover_tip(self, x, y, text):
        if self._hover_tip is None:
            self._hover_tip = tk.Toplevel(self.root)
            self._hover_tip.overrideredirect(True)
            self._hover_tip.attributes("-topmost", True)
            self._hover_tip_label = ttk.Label(
                self._hover_tip,
                text=text,
                background="#ffffe0",
                relief="solid",
                borderwidth=1,
                padding=(4, 2)
            )
            self._hover_tip_label.pack()
        else:
            self._hover_tip_label.config(text=text)

        self._hover_tip.geometry(f"+{x + 12}+{y + 12}")

    def _hide_hover_tip(self):
        if self._hover_tip is not None:
            self._hover_tip.destroy()
            self._hover_tip = None
            self._hover_tip_label = None

    # Mouse event handlers for crop movement and resizing via handles
    def on_canvas_down(self, event):
        if self.trans_pil is None:
            return
        self.dragging = True
        self.drag_start = (event.x, event.y)
        dx, dy = self.canvas_to_display(event.x, event.y)
        # decide if click is on handle
        x, y, side = self.crop
        corners = [(x, y), (x + side, y), (x + side, y + side), (x, y + side)]
        # find nearest corner within handle radius in display coords (converted to canvas coords)
        found_handle = None
        for i, (cx, cy) in enumerate(corners):
            hx, hy = self.display_to_canvas(cx, cy)
            if abs(hx - event.x) <= HANDLE_SIZE and abs(hy - event.y) <= HANDLE_SIZE:
                found_handle = i
                break
        if found_handle is not None:
            self.drag_type = f"handle-{found_handle}"
            self.crop_start = self.crop.copy()
            return
        # if click inside crop area (display coords)
        if x <= dx <= x + side and y <= dy <= y + side:
            self.drag_type = "move"
            self.crop_start = self.crop.copy()
            self.drag_offset_in_crop = (dx - x, dy - y)
            return
        self.drag_type = None

    def on_canvas_drag(self, event):
        if not self.dragging or self.drag_type is None:
            return
        dx, dy = self.canvas_to_display(event.x, event.y)
        x0, y0, side0 = self.crop_start
        iw, ih = self.trans_pil.size
        if self.drag_type == "move":
            offx, offy = self.drag_offset_in_crop
            nx = int(round(dx - offx))
            ny = int(round(dy - offy))
            nx = max(0, min(iw - side0, nx))
            ny = max(0, min(ih - side0, ny))
            self.crop = [nx, ny, side0]
        elif self.drag_type and self.drag_type.startswith("handle-"):
            handle_idx = int(self.drag_type.split("-")[1])
            # handles: 0 tl, 1 tr, 2 br, 3 bl
            # maintain square aspect: compute new side based on dragged corner opposite
            # base corner is opposite corner index (handle + 2) % 4
            opp_idx = (handle_idx + 2) % 4
            opp_corners = [(x0, y0), (x0 + side0, y0), (x0 + side0, y0 + side0), (x0, y0 + side0)]
            opp_x, opp_y = opp_corners[opp_idx]
            # new side length is max(abs(dx - opp_x), abs(dy - opp_y))
            new_side = int(round(max(abs(dx - opp_x), abs(dy - opp_y))))
            # compute new top-left depending on which handle
            if handle_idx == 0:  # tl
                nx = opp_x - new_side
                ny = opp_y - new_side
            elif handle_idx == 1:  # tr
                nx = opp_x
                ny = opp_y - new_side
            elif handle_idx == 2:  # br
                nx = opp_x
                ny = opp_y
            elif handle_idx == 3:  # bl
                nx = opp_x - new_side
                ny = opp_y
            # clamp within image
            nx = max(0, min(iw - new_side, nx))
            ny = max(0, min(ih - new_side, ny))
            new_side = max(1, min(min(iw - nx, ih - ny), new_side))
            self.crop = [int(nx), int(ny), int(new_side)]
        # update display
        self.redraw()
        # if show_prediction, debounce run segmentation
        if self.show_prediction_var.get():
            self._debounced_run()
        # always update classification if available (independent of segmentation checkbox)
        if self.classifier is not None:
            self._run_classification_on_current()
        # always update landmarks if available (independent of segmentation checkbox)
        if self.landmark_model is not None and self.show_landmarks_var.get():
            self._run_landmark_prediction_on_current()

    def on_canvas_up(self, event):
        self.dragging = False
        self.drag_type = None
        # final run segmentation if necessary
        if self.show_prediction_var.get():
            self._debounced_run()
        # always update classification if available (independent of segmentation checkbox)
        if self.classifier is not None:
            self._run_classification_on_current()
        # always update landmarks if available (independent of segmentation checkbox)
        if self.landmark_model is not None and self.show_landmarks_var.get():
            self._run_landmark_prediction_on_current()

    def cancel_drag(self):
        self.dragging = False
        self.drag_type = None
        self.crop_start = None
        self.redraw()

    # Rotation / flip handlers
    def on_rotation_change(self, val):
        try:
            # Accept negative values from slider (range -180..180). Keep exact integer.
            v = int(float(val))
        except:
            v = 0
        self.angle = v
        # recompute transformed image
        if self.raw_pil is None:
            return
        # To keep the crop in a consistent visual position, we'll map prior crop center to new transformed coordinate system.
        # Simpler approach: recompute transformed image, then try to keep crop center at same relative position of image center.
        old_trans = self.trans_pil
        old_crop = self.crop.copy() if self.crop else None
        old_tw, old_th = (old_trans.size if old_trans is not None else (0, 0))
        # compute center fraction of old crop relative to old trans
        if old_crop and old_tw > 0 and old_th > 0:
            cx = old_crop[0] + old_crop[2] / 2.0
            cy = old_crop[1] + old_crop[2] / 2.0
            frac_x = cx / old_tw
            frac_y = cy / old_th
        else:
            frac_x = 0.5
            frac_y = 0.5
        # update transformed image
        self.trans_pil = apply_transforms_to_image(self.raw_pil, self.angle, self.flip_h, self.brightness, self.contrast, self.smoothness, self.invert_colors)
        self.trans_size = self.trans_pil.size
        new_tw, new_th = self.trans_size
        # new crop keep same side if possible
        if old_crop:
            side = old_crop[2]
            # ensure side not larger than new min dim
            side = min(side, new_tw, new_th)
            # center using frac_x,y * new dims
            new_cx = int(round(frac_x * new_tw))
            new_cy = int(round(frac_y * new_th))
            nx = max(0, min(new_tw - side, int(round(new_cx - side / 2.0))))
            ny = max(0, min(new_th - side, int(round(new_cy - side / 2.0))))
            self.crop = [nx, ny, side]
        else:
            side = min(new_tw, new_th)
            self.crop = [(new_tw - side)//2, (new_th - side)//2, side]
        self.redraw()
        if self.show_prediction_var.get():
            self._debounced_run()
        # Re-run classification on new rotation
        if self.classifier is not None:
            self._run_classification_on_current()
        # Re-run landmark prediction on new rotation
        if self.landmark_model is not None and self.show_landmarks_var.get():
            self._run_landmark_prediction_on_current()

    def on_adjustment_change(self, val):
        """Handler for brightness, contrast, and smoothness slider changes."""
        try:
            self.brightness = float(self.brightness_var.get())
            self.contrast = float(self.contrast_var.get())
            self.smoothness = float(self.smoothness_var.get())
        except:
            pass
        if self.raw_pil is None:
            return
        # Recompute transformed image with new adjustments
        self.trans_pil = apply_transforms_to_image(self.raw_pil, self.angle, self.flip_h, self.brightness, self.contrast, self.smoothness, self.invert_colors)
        self.redraw()
        if self.show_prediction_var.get():
            self._debounced_run()
        # Re-run classification with new adjustments
        if self.classifier is not None:
            self._run_classification_on_current()
        # Re-run landmark prediction with new adjustments
        if self.landmark_model is not None and self.show_landmarks_var.get():
            self._run_landmark_prediction_on_current()

    def toggle_flip(self):
        self.flip_h = not self.flip_h
        # recompute transform while trying to preserve crop center similar to rotation handler
        old_crop = self.crop.copy() if self.crop else None
        old_tw, old_th = (self.trans_pil.size if self.trans_pil else (0, 0))
        if old_crop and old_tw > 0 and old_th > 0:
            cx = old_crop[0] + old_crop[2] / 2.0
            cy = old_crop[1] + old_crop[2] / 2.0
            frac_x = cx / old_tw
            frac_y = cy / old_th
        else:
            frac_x = 0.5; frac_y = 0.5
        self.trans_pil = apply_transforms_to_image(self.raw_pil, self.angle, self.flip_h, self.brightness, self.contrast, self.smoothness, self.invert_colors)
        self.trans_size = self.trans_pil.size
        new_tw, new_th = self.trans_size
        if old_crop:
            side = old_crop[2]
            side = min(side, new_tw, new_th)
            new_cx = int(round(frac_x * new_tw))
            new_cy = int(round(frac_y * new_th))
            nx = max(0, min(new_tw - side, int(round(new_cx - side / 2.0))))
            ny = max(0, min(new_th - side, int(round(new_cy - side / 2.0))))
            self.crop = [nx, ny, side]
        else:
            side = min(new_tw, new_th)
            self.crop = [(new_tw - side)//2, (new_th - side)//2, side]
        self.redraw()
        if self.show_prediction_var.get():
            self._debounced_run()
        # Re-run classification after flip
        if self.classifier is not None:
            self._run_classification_on_current()
        # Re-run landmark prediction after flip
        if self.landmark_model is not None and self.show_landmarks_var.get():
            self._run_landmark_prediction_on_current()
    
    def toggle_invert(self):
        self.invert_colors = not self.invert_colors
        self.trans_pil = apply_transforms_to_image(self.raw_pil, self.angle, self.flip_h, self.brightness, self.contrast, self.smoothness, self.invert_colors)
        self.redraw()
        if self.show_prediction_var.get():
            self._debounced_run()
        # Re-run classification after invert
        if self.classifier is not None:
            self._run_classification_on_current()
        # Re-run landmark prediction after invert
        if self.landmark_model is not None and self.show_landmarks_var.get():
            self._run_landmark_prediction_on_current()


    def reset_rotation(self):
        self.rot_scale.set(0)
        self.on_rotation_change(0)

    def reset_all_transforms(self):
        """Reset all transforms to defaults: rotation 0, no flip, brightness 1.0, contrast 1.0, smoothness 0.0, threshold 0.5"""
        self.rot_scale.set(0)
        self.flip_h = False
        self.invert_colors = False
        self.brightness_var.set(1.0)
        self.contrast_var.set(1.0)
        self.smoothness_var.set(0.0)
        self.threshold_var.set(DEFAULT_THRESHOLD)
        self.on_rotation_change(0)
        self.on_adjustment_change(None)
        self.on_threshold_change(DEFAULT_THRESHOLD)
        # Re-run classification if needed
        if self.classifier is not None:
            self._run_classification_on_current()
        # Re-run landmark prediction if needed
        if self.landmark_model is not None and self.show_landmarks_var.get():
            self._run_landmark_prediction_on_current()

    # Threshold
    def on_threshold_change(self, val):
        try:
            self.threshold = float(val)
        except:
            self.threshold = DEFAULT_THRESHOLD
        # If there is existing predicted probabilities, reapply binning & redraw overlays
        if self.last_pred_probs is not None:
            if self.last_pred_probs.ndim == 2:
                # Single channel
                self.last_pred_bin = (self.last_pred_probs >= self.threshold).astype(np.uint8) * 255
            else:
                # Multi-channel: binarize each channel independently
                bin_list = [(self.last_pred_probs[c] >= self.threshold).astype(np.uint8) * 255 
                           for c in range(self.last_pred_probs.shape[0])]
                self.last_pred_bin = np.stack(bin_list, axis=0)
            self.redraw()

    def reset_threshold(self):
        self.threshold_var.set(DEFAULT_THRESHOLD)
        self.on_threshold_change(DEFAULT_THRESHOLD)

    def reset_brightness(self):
        self.brightness_var.set(1.0)
        self.on_adjustment_change(None)

    def reset_contrast(self):
        self.contrast_var.set(1.0)
        self.on_adjustment_change(None)

    def reset_smoothness(self):
        self.smoothness_var.set(0.0)
        self.on_adjustment_change(None)

    # prediction controls
    def on_toggle_prediction(self):
        if self.show_prediction_var.get():
            # run if possible
            self._debounced_run()
        else:
            # clear cached pred
            self.last_pred_probs = None
            self.last_pred_bin = None
            self.redraw()

    def on_toggle_landmarks(self):
        if self.show_landmarks_var.get():
            # run landmark prediction if possible
            self._run_landmark_prediction_on_current()
        else:
            # clear cached landmarks
            self.last_landmarks_pred = None
            self.redraw()

    # handler for circular border checkbox
    def on_toggle_circular_border(self):
        """Handler for the Circular Border checkbox. Re-run classification and dependent predictions."""
        if self.circular_border_var.get():
            self.redraw()

        # Run classification to update decision
        if self.classifier is not None:
            self._run_classification_on_current()
        # Re-run segmentation if visible
        if self.show_prediction_var.get():
            self._debounced_run()
        # Re-run landmarks if visible
        if self.landmark_model is not None and self.show_landmarks_var.get():
            self._run_landmark_prediction_on_current()

    def on_toggle_mirror(self):
        """Handler for the Mirror Left checkbox. Re-run classification and dependent predictions."""
        # Run classification to update decision
        if self.classifier is not None:
            self._run_classification_on_current()
        # Re-run segmentation if visible
        if self.show_prediction_var.get():
            self._debounced_run()
        # Re-run landmarks if visible
        if self.landmark_model is not None and self.show_landmarks_var.get():
            self._run_landmark_prediction_on_current()

    def _classification_says_no_hip(self):
        """Return True if last_classification_result indicates a NO-HIP prediction.
        Be robust to different naming like 'NO-HIP', 'no_hip', 'no hip', or 'nohip'.
        """
        if self.last_classification_result is None:
            return False
        class_name = self.last_classification_result[0]
        if not isinstance(class_name, str):
            return False
        cn = class_name.lower().replace('_', ' ').replace('-', ' ').strip()
        # match phrases containing both 'no' and 'hip' or the concatenated form
        if 'no' in cn and 'hip' in cn:
            return True
        if 'nohip' in cn.replace(' ', ''):
            return True
        return False

    def _debounced_run(self):
        # Ensure classification runs first so mirror decision can be made
        if self.classifier is not None:
            try:
                self._run_classification_on_current()
            except Exception:
                pass
        if self._debounce_after_id:
            self.root.after_cancel(self._debounce_after_id)
        self._debounce_after_id = self.root.after(DEBOUNCE_MS, self._run_segmentation_on_current)
    
    def _run_classification_on_current(self):
        """Run classification on the cropped transformed image (same input as segmentation).
        This ensures classification is applied to the same region used for segmentation.
        """
        if self.classifier is None or self.trans_pil is None or self.crop is None:
            return

        try:
            # Use the same cropped region as segmentation
            x, y, side = self.crop
            crop_pil = self.trans_pil.crop((x, y, x + side, y + side))
            # Apply circular border if enabled
            if self.circular_border_var.get():
                crop_pil = apply_circular_border_to_image(crop_pil)
            inp = crop_pil.resize(IMAGE_SIZE, Image.BILINEAR)
            arr = np.asarray(inp).astype(np.float32) / 255.0
            t = torch.from_numpy(arr)[None, None, ...].float()
            t = t.cpu()

            # Run classification using tensor input
            class_name, percentage = self.classifier.predict_with_names(t, return_probs=True)
            self.last_classification_result = (class_name, percentage)
            # self.log(f"Classification: {class_name} {percentage}")
            self.redraw()
        except Exception as e:
            self.log("Classification error:", e)

    def _run_landmark_prediction_on_current(self):
        """Run landmark prediction on the cropped transformed image (same input as segmentation).
        Store results in last_landmarks_pred and redraw."""
        if self.landmark_model is None or self.trans_pil is None or self.crop is None:
            return
        
        try:
            # Use the same cropped region as segmentation
            x, y, side = self.crop
            crop_pil = self.trans_pil.crop((x, y, x + side, y + side))

            # Decide whether we need to mirror input based on classifier
            do_mirror = False
            try:
                if self.classifier is not None:
                    self._run_classification_on_current()
                if self.mirror_left_var.get() and self.last_classification_result is not None:
                    class_name, _ = self.last_classification_result
                    if isinstance(class_name, str) and "left" in class_name.lower():
                        do_mirror = True
            except Exception:
                do_mirror = False

            # If classifier guidance is enabled and classifier indicates NO-HIP, skip landmarks
            if self.mirror_left_var.get() and self.last_classification_result is not None:
                try:
                    if self._classification_says_no_hip():
                        # self.log("Classifier indicates NO-HIP; skipping landmark prediction as configured.")
                        self.last_landmarks_pred = None
                        self.redraw()
                        return
                except Exception:
                    pass

            crop_for_model = ImageOps.mirror(crop_pil) if do_mirror else crop_pil
            # Apply circular border if enabled
            if self.circular_border_var.get():
                crop_for_model = apply_circular_border_to_image(crop_for_model)

            # AnnotationModel.predict now accepts PIL.Image, numpy arrays, or torch tensors.
            # Pass the PIL image (resized to model image size if needed) directly to avoid temp files.
            # Ensure we pass the image in the same coordinate space as segmentation (use whole crop)
            try:
                pred = self.landmark_model.predict(crop_for_model, return_pixels=True, length=0.2)
            except TypeError:
                # Fallback: convert to numpy array then tensor
                arr = np.asarray(crop_for_model).astype(np.float32) / 255.0
                t = torch.from_numpy(arr)[None, None, ...].float().cpu()
                pred = self.landmark_model.predict(t, return_pixels=True, length=0.2)

            # If prediction was performed on a mirrored crop, flip landmark x-coordinates back
            if do_mirror and isinstance(pred, dict):
                pts = pred.get('points', {})
                vecs = pred.get('vectors', {})
                flipped_pts = {}
                for k, v in pts.items():
                    try:
                        px, py = float(v[0]), float(v[1])
                        flipped_px = float(side) - px
                        flipped_pts[k] = (flipped_px, py)
                    except Exception:
                        flipped_pts[k] = v
                flipped_vecs = {}
                for k, (anchor, end) in vecs.items():
                    try:
                        ax, ay = anchor
                        bx, by = end
                        f_ax = float(side) - float(ax)
                        f_bx = float(side) - float(bx)
                        flipped_vecs[k] = ((f_ax, ay), (f_bx, by))
                    except Exception:
                        flipped_vecs[k] = (anchor, end)
                pred['points'] = flipped_pts
                pred['vectors'] = flipped_vecs

            self.last_landmarks_pred = pred
            self.redraw()
        except Exception as e:
            self.log("Landmark prediction error:", e)

    def _run_segmentation_on_current(self):
        if self.model is None:
            messagebox.showwarning("No model", "No model loaded. Browse a model first.")
            return
        if self.trans_pil is None or self.crop is None:
            self.log("No image/crop to run.")
            return
        # get crop PIL (square) from transformed image
        x, y, side = self.crop
        crop_pil = self.trans_pil.crop((x, y, x + side, y + side))
        # Ensure classification result is available and decide whether to mirror input
        do_mirror = False
        try:
            if self.classifier is not None:
                # run classification to refresh last_classification_result
                self._run_classification_on_current()
            if self.mirror_left_var.get() and self.last_classification_result is not None:
                class_name, _ = self.last_classification_result
                if isinstance(class_name, str) and "left" in class_name.lower():
                    do_mirror = True
        except Exception:
            do_mirror = False

        # If classifier guidance is enabled and classifier indicates NO-HIP, skip segmentation
        if self.mirror_left_var.get() and self.last_classification_result is not None:
            try:
                if self._classification_says_no_hip():
                    self.log("Classifier indicates NO-HIP; skipping segmentation as configured.")
                    self.last_pred_probs = None
                    self.last_pred_bin = None
                    self.redraw()
                    return
            except Exception:
                pass
        # resize to IMAGE_SIZE expected by model
        try:
            # If mirroring is needed, flip the crop before sending to model (models trained on right-side hips)
            crop_for_model = ImageOps.mirror(crop_pil) if do_mirror else crop_pil
            # Apply circular border if enabled
            if self.circular_border_var.get():
                crop_for_model = apply_circular_border_to_image(crop_for_model)
            inp = crop_for_model.resize(IMAGE_SIZE, Image.BILINEAR)
            arr = np.asarray(inp).astype(np.float32) / 255.0
            # if image is grayscale shape HxW -> make 1x1xHWC
            t = torch.from_numpy(arr)[None, None, ...].float()
            t = t.to(self.device)
        except Exception as e:
            self.log("Preparing input failed:", e)
            return

        # run model
        try:
            with torch.no_grad():
                out = self.model(t)
            # out should be [1, C, H, W] where C is 1 (femur only) or 2 (femur + pelvis)
            out_np = out.cpu().squeeze().numpy().astype(np.float32)
            # Handle output shapes: [C, H, W] or [H, W] (1-channel)
            if out_np.ndim == 2:
                # Single channel output (femur only): shape (H, W)
                prob = cv2.resize(out_np, (side, side), interpolation=cv2.INTER_LINEAR)
                # If we ran on a mirrored input, flip probabilities back so they align with display
                if do_mirror:
                    prob = np.fliplr(prob)
                self.last_pred_probs = prob  # shape (side, side)
                self.last_pred_bin = (prob >= self.threshold).astype(np.uint8) * 255
            else:
                # Multi-channel output: shape (C, H, W) where C=2 for femur+pelvis
                # Store as (C, side, side) so visualization can handle multiple channels
                prob_list = []
                for c in range(out_np.shape[0]):
                    prob_c = cv2.resize(out_np[c], (side, side), interpolation=cv2.INTER_LINEAR)
                    if do_mirror:
                        prob_c = np.fliplr(prob_c)
                    prob_list.append(prob_c)
                self.last_pred_probs = np.stack(prob_list, axis=0)  # shape (C, side, side)
                # Binarize each channel
                bin_list = [(p >= self.threshold).astype(np.uint8) * 255 for p in prob_list]
                self.last_pred_bin = np.stack(bin_list, axis=0)  # shape (C, side, side)
            # self.log("Model run complete. Threshold:", self.threshold, "Output shape:", self.last_pred_probs.shape)
            self.redraw()
        except Exception as e:
            self.log("Model inference error:", e)
            return

    # saving predicted mask (aligned to raw image coordinates)
    def save_mask_dialog(self):
        if self.last_pred_bin is None:
            messagebox.showinfo("No prediction", "No predicted mask in memory. Run the model first.")
            return
        folder = os.path.dirname(self.current_path) if self.current_path else os.getcwd()
        base = os.path.splitext(os.path.basename(self.current_path))[0]
        default = os.path.join(folder, f"{base}_pred_mask.png")
        tgt = filedialog.asksaveasfilename(defaultextension=".png", initialfile=os.path.basename(default),
                                           filetypes=[("PNG", "*.png")], title="Save predicted mask")
        if not tgt:
            return
        self._save_pred_mask_to_path(tgt)

    def _save_pred_mask_to_path(self, outpath):
        # Build predicted mask in transformed-image coords
        x, y, side = self.crop
        tw, th = self.trans_pil.size
        raw_w, raw_h = self.raw_pil.size
        
        if self.last_pred_bin.ndim == 2:
            # Single-channel prediction (femur)
            pred_crop = self.last_pred_bin  # side x side
            # place into transformed-image sized array
            full_trans = np.zeros((th, tw), dtype=np.uint8)
            # if sizes mismatch (rare) resize pred_crop
            if pred_crop.shape[0] != side or pred_crop.shape[1] != side:
                pred_crop = cv2.resize(pred_crop, (side, side), interpolation=cv2.INTER_NEAREST)
            full_trans[y:y+side, x:x+side] = pred_crop
            # inverse transform to raw image coords
            mask_raw = inverse_transform_mask_on_canvas(full_trans, (tw, th), (x, y, side, side), self.angle, self.flip_h, (raw_w, raw_h))
            # ensure binary 0/255
            mask_raw = (mask_raw >= 128).astype(np.uint8) * 255
            try:
                cv2.imwrite(outpath, mask_raw)
                self.log("Saved predicted mask to", outpath)
                messagebox.showinfo("Saved", f"Saved predicted mask to:\n{outpath}")
            except Exception as e:
                self.log("Failed to save mask:", e)
                messagebox.showerror("Save error", str(e))
        else:
            # Multi-channel prediction (femur + pelvis): save as separate files
            base, ext = os.path.splitext(outpath)
            labels = [LABELS[m] for m in GT_KEYS if m in LABELS]
            try:
                for c in range(min(self.last_pred_bin.shape[0], len(labels))):
                    pred_crop = self.last_pred_bin[c]  # side x side
                    # place into transformed-image sized array
                    full_trans = np.zeros((th, tw), dtype=np.uint8)
                    # if sizes mismatch (rare) resize pred_crop
                    if pred_crop.shape[0] != side or pred_crop.shape[1] != side:
                        pred_crop = cv2.resize(pred_crop, (side, side), interpolation=cv2.INTER_NEAREST)
                    full_trans[y:y+side, x:x+side] = pred_crop
                    # inverse transform to raw image coords
                    mask_raw = inverse_transform_mask_on_canvas(full_trans, (tw, th), (x, y, side, side), self.angle, self.flip_h, (raw_w, raw_h))
                    # ensure binary 0/255
                    mask_raw = (mask_raw >= 128).astype(np.uint8) * 255
                    # save with label in filename
                    out_labeled = f"{base}_{labels[c]}{ext}"
                    cv2.imwrite(out_labeled, mask_raw)
                    self.log(f"Saved {labels[c]} mask to", out_labeled)
                messagebox.showinfo("Saved", f"Saved {self.last_pred_bin.shape[0]} masks for {', '.join(labels[:self.last_pred_bin.shape[0]])}")
            except Exception as e:
                self.log("Failed to save masks:", e)
                messagebox.showerror("Save error", str(e))

# run application
def main():
    root = tk.Tk()
    root.geometry("1500x830")
    app = SegmentationUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
