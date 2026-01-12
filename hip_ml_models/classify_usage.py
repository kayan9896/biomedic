from classify import ClassificationModel
# from hip_ml_models import ClassificationModel  # if installed using pip

# Initialize
classifier = ClassificationModel(model_path=r"\\Torus-NAS\Torus-Data\models\later_class_model.pth")

# Print model details
print(f"{classifier.get_task()} classification model with these classes: {classifier.get_class_names()}")

# Simple prediction
pred = classifier.predict(r"E:\augdrr_data\reference\Patient_1_R101782_borders\0\drr.png")
print(f"Predicted class index: {pred}")

# With probabilities
pred, probs = classifier.predict(r"E:\augdrr_data\reference\Patient_1_R101782_borders\0\drr.png", return_probs=True)
print(f"Predicted class index: {pred}, Probabilities: {probs}")

# With tensor input
# pred = classifier.predict(image_tensor)

# Human-readable output
class_name = classifier.predict_with_names(r"E:\augdrr_data\reference\Patient_1_R101782_borders\0\drr.png", return_probs=True)
print(f"Predicted class name: {class_name}")