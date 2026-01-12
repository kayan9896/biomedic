from segment import SegmentationModel
# from hip_ml_models import SegmentationModel  # if installed using pip

# Initialize
model = SegmentationModel(model_path=r"\\Torus-NAS\Torus-Data\models\ref_seg_model.pth")

# Single prediction
mask = model.predict(r"\\Torus-NAS\Torus-Data\augdrr_data\reference\Patient_1_R101782_borders\0\drr.png")

# Visualize with overlay
model.visualize_prediction(r"\\Torus-NAS\Torus-Data\augdrr_data\reference\Patient_1_R101782_borders\0\drr.png", show=True)

# Save masks
model.save_masks(r"\\Torus-NAS\Torus-Data\augdrr_data\reference\Patient_1_R101782_borders\0\drr.png", "D:/outputs")

# Batch process
model.batch_process("Test Scripts/Testing/other_drrs/", "D:/outputs_batch")