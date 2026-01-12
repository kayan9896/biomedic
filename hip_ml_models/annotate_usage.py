from annotate import AnnotationModel
# from hip_ml_models import AnnotationModel  # if installed using pip

# Initialize
annotator = AnnotationModel(model_path=r"\\Torus-NAS\Torus-Data\models\ref_lm_model.pth")

# Use the new predict() which returns labeled points and vectors
pred = annotator.predict(image=r"E:\augdrr_data\reference\Patient_1_R101782_borders\0\drr.png", return_pixels=True, readable_keys=True)
print("Predicted points:")
for k, v in pred.get("points", {}).items():
    print(f"  {k}: {v}")

print("\nPredicted vectors:")
for k, v in pred.get("vectors", {}).items():
    print(f"  {k}: {v}")

# Visualize overlay (saved to disk, do not display)
overlay = annotator.visualize(
    r"E:\augdrr_data\reference\Patient_1_R101782_borders\0\drr.png",
    pred=pred,
    show=False,
    save_path=r"D:\drr_overlay.png"
)
print("Saved visualization to:", r"D:\drr_overlay.png")

# Run visualize and show on screen (requires matplotlib)
annotator.visualize(r"E:\augdrr_data\reference\Patient_1_R101782_borders\0\drr.png", pred=pred, show=True)
