from .image_classifier import classifier
from .waste_mapper import map_label_to_waste
from app.core.config import settings
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Config: Minimum confidence to accept AI prediction
AI_CONFIDENCE_THRESHOLD = settings.AI_CONFIDENCE_THRESHOLD

def get_keyword_classification(filename: str) -> Dict[str, str]:
    """
    Existing keyword-based fallback logic (extracted from original code)
    """
    from app.core.config import WASTE_KEYWORDS
    fn = filename.lower()
    for cat, subs in WASTE_KEYWORDS.items():
        for sub, keywords in subs.items():
            if any(k in fn for k in keywords):
                return {
                    "category": cat,
                    "subcategory": sub,
                    "item_name": sub.title()
                }
    return {
        "category": "dry",
        "subcategory": "general waste",
        "item_name": "Unrecognized Item"
    }

def orchestrate_classification(image_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Run the AI classification pipeline with keywork-based fallback.
    """
    # 1. Run AI
    label, confidence = classifier.predict(image_bytes)
    
    # 2. Check confidence
    if confidence >= AI_CONFIDENCE_THRESHOLD:
        mapped = map_label_to_waste(label)
        logger.info(f"AI Success: {label} ({confidence:.2f}) -> {mapped['category']}")
        return {
            "predicted_label": label,
            "confidence_score": round(confidence, 4),
            "classification_source": "ai_model",
            "category": mapped["category"],
            "subcategory": mapped["subcategory"],
            "item_name": mapped["item_name"]
        }
    
    # 3. Fallback to keywords
    logger.warning(f"AI Uncertain: {label} ({confidence:.2f}) < {AI_CONFIDENCE_THRESHOLD}. Using fallback.")
    fallback = get_keyword_classification(filename)
    
    return {
        "predicted_label": label if confidence > 0.1 else "Unknown",
        "confidence_score": round(confidence, 4),
        "classification_source": "fallback",
        "category": fallback["category"],
        "subcategory": fallback["subcategory"],
        "item_name": fallback["item_name"] if fallback["category"] != "dry" else "General Waste"
    }
