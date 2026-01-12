"""
Example usage script for the unified HipModels wrapper.
It can be used for classification, segmentation, and annotation of hip images.

1) Classification
label_int = models.classify(IMAGE_PATH)
label_text = models.classify(IMAGE_PATH, human_readable=True)

3) Segmentation example (ref/cup/trial), uses classification by default to guide predictions (flip_if_left=True and/or only_if_hip=True)
seg_mask = models.segment(IMAGE_PATH, phase="ref")

4) Annotation example, disable classification guidance by setting only_if_hip=False and/or flip_if_left=False. You can also set readable_keys=True to get more human-friendly point/vector names.
annot = models.annotate(IMAGE_PATH, phase="ref", flip_if_left=False, only_if_hip=False)

5) results can be none if no hip detected (only_if_hip=True)
if annot is None:
    print("Annotation skipped → NO-HIP detected.\n")
else:
    print("Points:")
    for name, pt in annot["points"].items():
        print(f"  {name}: {pt}")
    print("\nVectors:")
    for (a, b), (p1, p2) in annot["vectors"].items():
        print(f"  {a}->{b}: {p1} → {p2}")

6) Change phase: 
- if ref was loaded, choosing all will load cup and trial models only.
- if all was loaded, choosing cup will unload ref and trial models.
- if cup was loaded, choosing ref will unload cup and load ref only.
"""

from hip_models import HipModels , HipModelConfig

# -----------------------------------------------------------
# Configuration
# -----------------------------------------------------------
IMAGE_PATH = r"E:\augdrr_data\reference\Patient_1_R101782_borders\0\drr.png"

# 0) Define configuration, below are the default model names and directory, so you can use it like this cfg = HipModelConfig()
cfg = HipModelConfig(
    model_dir=r"\\Torus-NAS\Torus-Data\models",

    later_cls_name = "later_class_model.pth",
    phase_cls_name = "phase_class_model.pth",

    ref_seg_name = "ref_seg_model.pth",
    cup_seg_name = "cup_seg_model.pth",
    trial_seg_name = "trial_seg_model.pth",

    ref_lm_name = "ref_lm_model.pth",
    cup_lm_name = "cup_lm_model.pth",
    trial_lm_name = "trial_lm_model.pth",

    phase="ref",   # "all", "ref", "cup", "trial"
)

# 1) Initialize wrapper class
models = HipModels(config=cfg)        

# 2) prediction example
predictions = models.predict(IMAGE_PATH, phase='ref')
for key, value in predictions.items():
    print(f"\n{key}: {value}\n", end="="*40 + "\n")

# 3) Change phase example
models.update_phase("cup")
print(f"Phase updated to {models.phase}.")
