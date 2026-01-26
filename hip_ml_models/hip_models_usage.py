"""
Example usage script for the unified HipModels wrapper.
It can be used for classification, segmentation, and annotation of hip images.

Code by Maad Ebrahim for Torus Biomedical Inc., 2025-2027.

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
from confirmap_dataclasses import *

# -----------------------------------------------------------
# Configuration
# -----------------------------------------------------------
IMAGE_PATH = r"\\Torus-NAS\Torus-Data\augdrr_data\reference\Patients_1_to_4_v023\7296\drr.png"

# 1) Configure
frame_prediction_config = FramePredictionConfigClass(
    classifier_model_path=r"\\Torus-NAS\Torus-Data\models\later_class_model.pth",
    ref_annotator_model_path=r"\\Torus-NAS\Torus-Data\models\ref_lm_model.pth",
    ref_segmentor_model_path=r"\\Torus-NAS\Torus-Data\models\ref_seg_model.pth",
    cup_annotator_model_path=r"\\Torus-NAS\Torus-Data\models\cup_lm_model.pth",
    cup_segmentor_model_path=r"\\Torus-NAS\Torus-Data\models\cup_seg_model.pth",
    trl_annotator_model_path=r"\\Torus-NAS\Torus-Data\models\trial_lm_model.pth",
    trl_segmentor_model_path=r"\\Torus-NAS\Torus-Data\models\trial_seg_model.pth",
)

# 2) Initialize
models = HipModels(frame_config=frame_prediction_config, device="cpu")      # device is optional  

# --- frame ---
frame = Frame()
frame.meta = FrameMeta(
    op_stage='hp1-ap',   # ref: 'hp1-ap', 'hp1-ob', 'hp2-ap', 'hp2-ob' ||| cup: 'cup-ap', 'cup-ob' ||| trial: 'tri-ap', 'tri-ob'
    image_filename=IMAGE_PATH,
)

# 3) predict
frame.annotations["predictions"] = models.predict(frame=frame)
print(frame)