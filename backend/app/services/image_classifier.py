import torch
import torchvision.transforms as T
from torchvision.models import mobilenet_v2, MobileNet_V2_Weights
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

# Initialize model once globally (Singleton-ish)
class ImageClassifier:
    def __init__(self):
        self.weights = MobileNet_V2_Weights.IMAGENET1K_V1
        self.model = mobilenet_v2(weights=self.weights)
        self.model.eval()
        self.preprocess = self.weights.transforms()
        self.categories = self.weights.meta["categories"]
        logger.info("AI Image Classifier (MobileNetV2) initialized successfully.")

    def predict(self, image_bytes: bytes) -> tuple[str, float]:
        """
        Runs inference on uploaded image bytes.
        Returns: (top_label, confidence_score)
        """
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            # Apply preprocessing
            batch = self.preprocess(image).unsqueeze(0)
            
            # Predict
            with torch.no_grad():
                prediction = self.model(batch).squeeze(0).softmax(0)
                conf, class_id = torch.max(prediction, dim=0)
                
            label = self.categories[class_id.item()]
            return label, conf.item()
            
        except Exception as e:
            logger.error(f"Image classification failed: {e}")
            return "Unknown", 0.0

# Create a singleton instance
classifier = ImageClassifier()
