<!--
AI Modules Repository

This repository provides modular, production-ready machine learning models for hip imaging analysis, including
segmentation, classification, and landmark detection. It also includes a unified inference wrapper that combines
all models into a single interface and an optional graphical user interface for development-time evaluation and
visualization.

Code by Maad Ebrahim for Torus Biomedical Inc., 2025-2027.

The package is designed for easy installation, CPU-first compatibility, optional CUDA acceleration, and clear,
example-driven usage for both standalone modules and the unified pipeline.
-->

# AI Modules Repository

This repository contains machine learning modules under `hip_ml_models` for hip imaging analysis:

- Segmentation
- Classification
- Landmark detection
- A unified wrapper for all three models
- A graphical user interface for model evaluation and visualization

## Installation

The package can be installed directly from GitHub:
```powershell
pip install git+https://github.com/Torus-Biomedical-Solutions/hip_ml_models.git@main
```

To reinstall (update) an existing installation without changing dependencies:
```powershell
pip install --force-reinstall --no-deps git+https://github.com/Torus-Biomedical-Solutions/hip_ml_models.git@main
```

This installs a CPU-only PyTorch build by default, ensuring a working setup on any machine. GPU (CUDA) support can be enabled **before** installation or **afterward** if desired (Check **PyTorch and CUDA Support** Section below).

## Repository Contents

**Files of interest**
- `segment.py` — model definition (`UNet` and related classes), inference wrapper (`SegmentationModel`), and utilities for visualization and saving masks
- `segment_usage.py` — usage example for the segmentation module (not installed)
- `classify.py` — model definition (pretrained `ResNet18`), inference wrapper (`ClassificationModel`), and utilities for predictions with class names and confidence percentage
- `classify_usage.py` — usage example for the classifcation module (not installed)
- `annotate.py` — model definition (pretrained `ResNet18` with attention channels and two heads for points and axis directions) and inference wrapper (`AnnotationModel`)
- `annotate_usage.py` — usage example for the landmark detection module (not installed)
- `hip_models.py` — unified wrapper for all three models; can automatically handle laterality (via classification). Future implementation can allow it to also autmatically handle phase selection (using a phase detection model)
- `hip_models_usage.py` — usage example for the unified wrapper (not installed)
- `inference_ui.py` — interactive visualization UI for predictions and ground-truth overlays (development/validation only; not installed)


The following files are **not included** in the installed package:
- `inference_ui.py`
- `onnx_exporter.py`
- `*_usage.py`

## Graphical User Interface

The `inference_ui.py` tool provides an interactive visualization interface for models' predictions during development.

It allows visual comparison of predictions from different models and comparison with ground truth (if available).

The UI is useful for:
- validating model outputs
- demonstrating robustness to transformations (rotation, brightness, contrast, smoothing, cropping)

It is **not required** for deploying the prediction modules.


## Requirements
**Tested with Python 3.11.13**

This project has two types of dependencies:

1. **Core Python packages** (installed automatically when installing the repo)
2. **PyTorch** (installed as CPU by default; CUDA optional)

### Core dependencies
Installed automatically via `pip install`:
- `opencv-python==4.12.0.88`
- `numpy==2.2.6`
- `Pillow==11.3.0`
- `matplotlib==3.10.6`

## PyTorch and CUDA Support
By default, installing `hip_ml_models` installs **CPU-only PyTorch**:
- `torch==2.7.1`
- `torchvision==0.22.1`

This guarantees the package works immediately.

### Enabling GPU (CUDA)
The models were trained with CUDA 11.8: `torch==2.7.1+cu118` and `torchvision==0.22.1+cu118`.

If you have a compatible NVIDIA GPU, install PyTorch with CUDA **before** installing `hip_ml_models`:
```powershell
pip install torch==2.7.1+cu118 torchvision==0.22.1+cu118 --index-url https://download.pytorch.org/whl/cu118
```

You can also reinstall PyTorch with CUDA **after** installing `hip_ml_models`:
```powershell
pip install --force-reinstall --no-deps torch==2.7.1+cu118 torchvision==0.22.1+cu118 --index-url https://download.pytorch.org/whl/cu118
```

To verify CUDA availability after installing PyTorch with CUDA:
```powershell
python -c "import torch; print(torch.cuda.is_available())"
```

To verify Torch version:
```powershell
python -c "import torch; print(torch.__version__)"
```

Refer to the official PyTorch guide for other CUDA versions:\
https://pytorch.org/get-started/locally/




## Segmentation Module: Usage for Inference

```python
from segment import SegmentationModel
# from hip_ml_models import SegmentationModel  # if installed using pip

# Initialize: model_path must point to a saved .pth 
model = SegmentationModel(model_path=r"path/to_model/mode_name.pth", image_size=(256,256))

# Single image prediction (binary mask or multi-channel masks)
mask = model.predict(r"path/to/image.png", threshold=0.5)

# Get probabilities and masks
probs, masks = model.predict(r"path/to/image.png", return_probs=True)

# Visualize (saves overlay if save_path given)
viz = model.visualize_prediction(r"path/to/image.png", threshold=0.5, save_path=r"pred_viz.png", show=True)

# Save predicted mask files
saved_paths = model.save_masks(r"path/to/image.png", r"predictions/", threshold=0.5)

# Batch process a directory
all_saved = model.batch_process(r"images/", r"masks/")
```

### Running the segmentation example

```powershell
python hip_ml_models/segment.py
python hip_ml_models/segment_usage.py
```

## Classification Module: Usage for Inference

```python
from classify import ClassificationModel
# from hip_ml_models import ClassificationModel  # if installed using pip

# Initialize
classifier = ClassificationModel(model_path=r"path/to_model/mode_name.pth")

# Simple prediction
pred = classifier.predict(r"path/to/image.png")
print(f"Predicted class index: {pred}")

# With probabilities
pred, probs = classifier.predict(r"path/to/image.png", return_probs=True)
print(f"Predicted class index: {pred}, Probabilities: {probs}")

# With tensor input
# pred = classifier.predict(image_tensor)

# Human-readable output
class_name = classifier.predict_with_names(r"path/to/image.png", return_probs=True)
print(f"Predicted class name: {class_name}")
```

### Running the classification example
```powershell
python hip_ml_models/classify.py
python hip_ml_models/classify_usage.py
```

## Landmark Detection Module: Usage for Inference

```python
from annotate import AnnotationModel
# from hip_ml_models import AnnotationModel  # if installed using pip

# Initialize
annotator = AnnotationModel(model_path=r"path/to_model/mode_name.pth")

# Use the new predict() which returns labeled points and vectors
pred = annotator.predict(image=r"path/to/image.png", return_pixels=True, readable_keys=True)
print("Predicted points:")
for k, v in pred.get("points", {}).items():
    print(f"  {k}: {v}")

print("\nPredicted vectors:")
for k, v in pred.get("vectors", {}).items():
    print(f"  {k}: {v}")

# Visualize overlay (saved to disk, do not display)
overlay = annotator.visualize(
    r"path/to/image.png",
    pred=pred,
    show=False,
    save_path=r"D:\drr_overlay.png"
)
print("Saved visualization to:", r"D:\drr_overlay.png")

# Run visualize and show on screen (requires matplotlib)
annotator.visualize(r"path/to/image.png", pred=pred, show=True)
```

### Running the landmark detection example
```powershell
python hip_ml_models/annotate.py
python hip_ml_models/annotate_usage.py
```


## Unified Modules Wrapper: Usage for Inference
```python
from hip_models import HipModels
# from hip_ml_models import HipModels  # if installed using pip

IMAGE_PATH = r"path/to/image.png"

# 1) Initialize wrapper 
models = HipModels()      

# 2) prediction example
predictions = models.predict(IMAGE_PATH, phase='ref')
for key, value in predictions.items():
    print(f"\n{key}: {value}\n", end="="*40 + "\n")

# 3) Change phase example
models.update_phase("cup")
print(f"Phase updated to {models.phase}.")
```

### Running the wrapper example
```powershell
python hip_ml_models/hip_models_usage.py
```

## Importing **installed** `hip_ml_models` package

```python
from hip_ml_models import HipModels
```

## Downloading Trained Models
All models will be stored on NAS:\
`\\Torus-NAS\Torus-Data\models`

### Segmentation Models
- Reference Phase: `ref_seg_model.pth`.
- Cup Phase: `cup_seg_model.pth`.
- Trial Phase: `trial_seg_model.pth`.

### Classification Model
- All Phases: `class_model.pth`

### Landmark Detection Models
- Reference Phase: `ref_lm_model.pth`.
- Cup Phase: `cup_lm_model.pth`.
- Trial Phase: `trial_lm_model.pth`.

## Troubleshooting
- If the version matches `2.7.1` without a CUDA suffix, the CPU build is installed and working correctly.

- If CUDA is required, (re)install PyTorch with the appropriate CUDA wheel.

- If the version number does not match, model loading warnings or errors may occur.
