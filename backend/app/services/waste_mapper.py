from typing import Dict, Tuple

# Mapping raw model labels to WasteWise categories and subcategories
# Format: { "raw_label_keyword": ("waste_type", "subcategory", "item_name") }
WASTE_LABEL_MAP: Dict[str, Tuple[str, str, str]] = {
    "water_bottle": ("dry", "plastic", "Plastic Bottle"),
    "plastic_bottle": ("dry", "plastic", "Plastic Bottle"),
    "pill_bottle": ("dry", "plastic", "Pill Bottle"),
    "wine_bottle": ("dry", "glass", "Glass Bottle"),
    "beer_bottle": ("dry", "glass", "Glass Bottle"),
    "glass_bottle": ("dry", "glass", "Glass Bottle"),
    "coffee_mug": ("dry", "glass", "Ceramic Mug"),
    "banana": ("wet", "food", "Banana Peel"),
    "apple": ("wet", "food", "Fruit Waste"),
    "orange": ("wet", "food", "Fruit Waste"),
    "lemon": ("wet", "food", "Fruit Waste"),
    "corn": ("wet", "food", "Corn Cob"),
    "pineapple": ("wet", "food", "Pineapple Skin"),
    "plate": ("dry", "glass", "Ceramic Plate"),
    "fork": ("dry", "metal", "Metal Cutlery"),
    "spoon": ("dry", "metal", "Metal Cutlery"),
    "knife": ("dry", "metal", "Metal Cutlery"),
    "laptop": ("e-waste", "laptop", "Laptop Computer"),
    "notebook_computer": ("e-waste", "laptop", "Laptop Computer"),
    "computer_keyboard": ("e-waste", "electronics", "Computer Keyboard"),
    "mouse": ("e-waste", "electronics", "Computer Mouse"),
    "mobile_phone": ("e-waste", "mobile", "Smartphone"),
    "cellular_telephone": ("e-waste", "mobile", "Smartphone"),
    "ipod": ("e-waste", "mobile", "Electronic Device"),
    "battery": ("hazardous", "battery", "Battery"),
    "cardboard": ("dry", "paper", "Cardboard Box"),
    "carton": ("dry", "paper", "Carton"),
    "paper_towel": ("dry", "paper", "Paper Waste"),
    "book": ("dry", "paper", "Book/Magazine"),
    "newspaper": ("dry", "paper", "Newspaper"),
    "envelope": ("dry", "paper", "Envelope"),
    "shirt": ("dry", "cloth", "Old Clothing"),
    "jeans": ("dry", "cloth", "Textile Waste"),
    "jersey": ("dry", "cloth", "Clothing"),
    "sock": ("dry", "cloth", "Textile Waste"),
    "can": ("dry", "metal", "Metal Can"),
    "pop_bottle": ("dry", "plastic", "Plastic Bottle"),
    "soda_can": ("dry", "metal", "Soda Can"),
    "hamster": ("wet", "garden", "Organic Waste"), # Sometimes models misidentify garden things
    "leaf": ("wet", "garden", "Leaf/Garden Waste"),
}

def map_label_to_waste(raw_label: str) -> Dict:
    """
    Map a raw label (from ImageNet/AI model) into its WasteWise category and subcategory.
    Returns: { 'category', 'subcategory', 'item_name', 'normalized_label' }
    """
    normalized = raw_label.lower().replace(" ", "_")
    
    # Check for direct match first
    if normalized in WASTE_LABEL_MAP:
        res = WASTE_LABEL_MAP[normalized]
        return {
            "category": res[0],
            "subcategory": res[1],
            "item_name": res[2],
            "normalized_label": normalized
        }
    
    # Check for partial keyword match
    for keyword, info in WASTE_LABEL_MAP.items():
        if keyword in normalized or normalized in keyword:
            return {
                "category": info[0],
                "subcategory": info[1],
                "item_name": info[2],
                "normalized_label": normalized
            }
            
    # Default fallback within mapping logic
    return {
        "category": "dry",
        "subcategory": "general waste",
        "item_name": raw_label.title().replace("_", " "),
        "normalized_label": normalized
    }
