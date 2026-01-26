"""
Classification Model Wrapper
A self-contained module for loading and running inference with a trained classification model.

Code by Maad Ebrahim for Torus Biomedical Inc., 2025-2027.

Usage:
    from classify import ClassificationModel
    
    # Initialize model
    classifier = ClassificationModel(model_path="path/to/model.pth")
    
    # Predict from image path
    pred = classifier.predict("path/to/image.png")
    
    # Predict from tensor with probabilities
    pred, probs = classifier.predict(image_tensor, return_probs=True)
"""

import os
import torch
import torch.nn as nn
import torchvision.models as models
import cv2
import numpy as np
from pathlib import Path
from typing import Any, Union, Tuple, Optional

try:
    from PIL import Image
except Exception:
    Image = None


class ClassificationModel:
    """
    Hip laterality classification model wrapper.
    
    Classes:
        0 → RIGHT HIP
        1 → LEFT HIP
        2 → NO-HIP
    """
    
    # CLASS_NAMES = {
    #     0: "RIGHT HIP",
    #     1: "LEFT HIP",
    #     2: "NO-HIP"
    # }
    
    def __init__(
        self,
        model_path: str,
        num_classes: int = 3,
        image_size: Tuple[int, int] = (256, 256),
        device: Optional[str] = None,
    ):
        """
        Initialize the classification model.
        
        Args:
            model_path: Path to the saved model weights (.pth file)
            num_classes: Number of output classes (default: 3)
            image_size: Target image size for inference (default: (256, 256))
            device: Device to run model on ('cuda', 'cpu', or None for auto-detect)
        
        Raises:
            FileNotFoundError: If model_path does not exist
            RuntimeError: If model loading fails
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        # Set device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
                
        # self.image_size = image_size
        # self.num_classes = num_classes
        
        # Build model
        # self.model = self._build_model(num_classes)
        
        # Load weights
        try:
            # state_dict = torch.load(model_path, map_location=self.device)
            # self.model.load_state_dict(state_dict)
            ckpt = torch.load(model_path, map_location=self.device)

            # Backward compatibility for legacy checkpoints
            ckpt = self._upgrade_legacy_checkpoint(ckpt)

            if ckpt.get("legacy", False):
                upgraded_path = Path(model_path).with_suffix(".upgraded.pth")

                torch.save(
                    {
                        "state_dict": ckpt["state_dict"],
                        "task": ckpt["task"],
                        "class_names": ckpt["class_names"],
                        "num_classes": ckpt["num_classes"],
                        "image_size": ckpt["image_size"],
                    },
                    upgraded_path,
                )

                print(f"Upgraded legacy checkpoint saved to: {upgraded_path}")

            if "state_dict" not in ckpt:
                raise RuntimeError(
                    "Invalid checkpoint format. Expected a dict with key 'state_dict'."
                )

            # Metadata from training
            self.task = ckpt.get("task", "unknown")
            self.class_names = ckpt.get("class_names")
            self.num_classes = ckpt.get("num_classes", num_classes)
            self.image_size = tuple(ckpt.get("image_size", image_size))

            if self.class_names is None:
                raise RuntimeError("Checkpoint missing 'class_names'")

            # Build and load model 
            self.model = self._build_model(self.num_classes)
            self.model.load_state_dict(ckpt["state_dict"])

            print(f"{self.task} classification model loaded from ({model_path}) to ({self.device})")
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}")
        
        # Move to device and set to eval mode
        self.model = self.model.to(self.device)
        self.model.eval()
    
    def _build_model(self, num_classes: int) -> nn.Module:
        """Build ResNet18 model with single-channel input."""
        model = models.resnet18()  # weights="IMAGENET1K_V1"
        
        # Adapt for single-channel (grayscale) input
        model.conv1 = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
        
        # Replace classifier
        model.fc = nn.Linear(model.fc.in_features, num_classes)
        
        return model
    
    def _upgrade_legacy_checkpoint(self, ckpt):
        """
        Upgrade legacy checkpoints (state_dict only) by injecting laterality metadata.
        Temporary compatibility layer.
        """
        legacy = False

        # Case 1: raw state_dict (no wrapper dict)
        if isinstance(ckpt, dict) and "state_dict" not in ckpt:
            ckpt = {"state_dict": ckpt}
            legacy = True

        # Missing metadata → legacy
        required_keys = {"task", "class_names", "num_classes", "image_size"}
        if not required_keys.issubset(ckpt.keys()):
            legacy = True

        if legacy:
            # Inject defaults if missing
            ckpt.setdefault("task", "laterality")
            ckpt.setdefault("class_names", ["RIGHT HIP", "LEFT HIP", "NO-HIP"])
            ckpt.setdefault("num_classes", 3)
            ckpt.setdefault("image_size", (256, 256))
        
        ckpt["legacy"] = legacy

        return ckpt


    def _load_image(self, image_path: str) -> np.ndarray:
        """
        Load and preprocess image from file path.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Preprocessed image as numpy array (float32, normalized to [0, 1])
            
        Raises:
            FileNotFoundError: If image file not found
            RuntimeError: If image loading fails
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        try:
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                raise RuntimeError(f"Failed to load image: {image_path}")
            
            # Resize to target size
            img = cv2.resize(img, self.image_size)
            
            # Normalize to [0, 1]
            img = img.astype(np.float32) / 255.0
            
            return img
        except Exception as e:
            raise RuntimeError(f"Error loading image {image_path}: {e}")
    
    def _prepare_tensor(self, image: Any) -> torch.Tensor:
        """
        Convert image to model input tensor.
        
        Args:
            image: Image path (str), numpy array, or torch tensor
            
        Returns:
            Tensor of shape (1, 1, H, W) ready for model input
        """
        # Support: path (str/Path), PIL.Image, numpy.ndarray, torch.Tensor
        img_array = None

        # Path or str -> use existing loader (which returns float32 [0..1] and resized)
        if isinstance(image, (str, Path)):
            img_array = self._load_image(str(image))

        # PIL Image -> convert to grayscale and numpy
        elif Image is not None and isinstance(image, Image.Image):
            pil = image.convert("L")
            arr = np.asarray(pil).astype(np.float32) / 255.0
            if arr.shape != self.image_size:
                arr = cv2.resize(arr, self.image_size)
            img_array = arr

        # Torch Tensor -> convert to numpy then handle
        elif isinstance(image, torch.Tensor):
            t = image.detach().cpu()
            # If already batch x channel x H x W with correct channel, return
            if t.dim() == 4 and t.shape[1] == 1:
                return t.to(self.device)
            # If single 2D image
            if t.dim() == 2:
                arr = t.numpy().astype(np.float32)
                if arr.max() > 1.0:
                    arr = arr / 255.0
                if arr.shape != self.image_size:
                    arr = cv2.resize(arr, self.image_size)
                img_array = arr
            # If channels-first (C,H,W)
            elif t.dim() == 3:
                if t.shape[0] in (1, 3, 4):
                    t = t.permute(1, 2, 0)
                arr = t.numpy().astype(np.float32)
                if arr.max() > 1.0:
                    arr = arr / 255.0
                # If multi-channel, collapse to grayscale by averaging RGB
                if arr.ndim == 3 and arr.shape[2] in (3, 4):
                    arr = arr[..., :3].mean(axis=2)
                if arr.shape != self.image_size:
                    arr = cv2.resize(arr, self.image_size)
                img_array = arr
            else:
                raise ValueError(f"Unsupported tensor shape: {t.shape}")

        # numpy array
        elif isinstance(image, np.ndarray):
            arr = image.astype(np.float32)
            # channels-first -> (H,W,C)
            if arr.ndim == 3 and arr.shape[0] in (1, 3, 4) and arr.shape[0] < arr.shape[1]:
                arr = np.transpose(arr, (1, 2, 0))
            if arr.max() > 1.0:
                arr = arr / 255.0
            # if multi-channel, average channels to grayscale
            if arr.ndim == 3 and arr.shape[2] in (3, 4):
                arr = arr[..., :3].mean(axis=2)
            if arr.ndim == 2 and arr.shape != self.image_size:
                arr = cv2.resize(arr, self.image_size)
            img_array = arr

        else:
            raise TypeError(f"Unsupported image type: {type(image)}")

        # At this point img_array should be a float32 numpy array in [0..1] shaped (H, W)
        if img_array is None:
            raise RuntimeError("Failed to prepare image tensor")

        tensor = torch.from_numpy(img_array[None, None, ...].astype(np.float32))
        return tensor.to(self.device)
    
    def predict(
        self,
        image: Any,
        return_probs: bool = False,
    ) -> Union[int, Tuple[int, float]]:
        """
        Run inference on an image.
        
        Args:
            image: Image path, numpy array, or torch tensor
            return_probs: If True, return (prediction, probability of prediction)
            
        Returns:
            If return_probs=False: predicted class index (0, 1, or 2)
            If return_probs=True: tuple of (class index, probability of predicted class)
            
        Examples:
            # Predict from path
            pred = classifier.predict("image.png")
            
            # Predict from tensor with probabilities
            pred, prob = classifier.predict(image_tensor, return_probs=True)
        """
        # Prepare input
        tensor = self._prepare_tensor(image)
        
        # Forward pass
        with torch.no_grad():
            logits = self.model(tensor)
            probabilities = torch.softmax(logits, dim=1)
        
        # Get prediction
        pred = torch.argmax(probabilities, dim=1).item()
        
        if return_probs:
            prob = probabilities[0, pred].item()
            return pred, prob
        
        return pred
    
    def predict_batch(
        self,
        images: list[Any],
        return_probs: bool = False,
    ) -> Union[list, Tuple[list, list]]:
        """
        Run inference on multiple images.
        
        Args:
            images: List of image paths, numpy arrays, or torch tensors
            return_probs: If True, return (predictions, probabilities of predictions)
            
        Returns:
            If return_probs=False: list of predicted class indices
            If return_probs=True: tuple of (predictions list, list of probabilities)
        """
        predictions = []
        all_probs = []
        
        for image in images:
            if return_probs:
                pred, prob = self.predict(image, return_probs=True)
                all_probs.append(prob)
            else:
                pred = self.predict(image, return_probs=False)
            
            predictions.append(pred)
        
        if return_probs:
            return predictions, all_probs
        
        return predictions
    
    def get_class_name(self, class_idx: int) -> str:
        """Get human-readable class name."""
        if 0 <= class_idx < len(self.class_names):
            return self.class_names[class_idx]
        return f"Unknown ({class_idx})"
        # return self.CLASS_NAMES.get(class_idx, f"Unknown ({class_idx})")
    
    def get_class_names(self) -> list[str]:
        return list(self.class_names)

    def get_task(self) -> str:
        return self.task

    def predict_with_names(
        self,
        image: Any,
        return_probs: bool = False,
    ) -> Union[str, Tuple[str, str]]:
        """
        Run inference and return human-readable class names.
        
        Args:
            image: Image path, numpy array, or torch tensor
            return_probs: If True, return (class name, percentage probability of prediction)
            
        Returns:
            If return_probs=False: class name string
            If return_probs=True: tuple of (class name, percentage string with % symbol)
        """
        if return_probs:
            pred, prob = self.predict(image, return_probs=True)
            percentage = f"{prob * 100.0:.2f}%"
            return self.get_class_name(pred), percentage
        else:
            pred = self.predict(image)
            return self.get_class_name(pred)


if __name__ == "__main__":
    """Example usage"""
    # Example: Initialize and use the model
    print("Classification Model Example")
    print("=" * 50)
    
    # This is just an example structure
    # In practice, replace with your actual model path and image path
    
    example_model_path = "path/to/best_classification.pth"
    example_image_path = "path/to/test_image.png"
    
    if os.path.exists(example_model_path) and os.path.exists(example_image_path):
        # Initialize model
        classifier = ClassificationModel(model_path=example_model_path)
        
        # Single prediction
        print("\n1. Prediction from image path:")
        pred = classifier.predict(example_image_path)
        print(f"   Predicted class: {pred} ({classifier.get_class_name(pred)})")
        
        # Prediction with probabilities
        print("\n2. Prediction with probabilities:")
        pred, prob = classifier.predict(example_image_path, return_probs=True)
        print(f"   Predicted class: {pred}")
        print(f"   Probability: {prob:.4f} ({prob*100:.2f}%)")
        
        # Human-readable prediction
        print("\n3. Prediction with class names:")
        class_name, percentage = classifier.predict_with_names(example_image_path, return_probs=True)
        print(f"   Predicted: {class_name}")
        print(f"   Confidence: {percentage}")
    else:
        print("\nNote: To run this example, provide valid paths to:")
        print(f"  - Model: {example_model_path}")
        print(f"  - Image: {example_image_path}")
