import time
from typing import Any

REQUIRED_FIELDS = {
    "GENERAL": ["product_name","net_quantity","manufacturer_name","manufacturer_address",
                "country_of_origin","mrp","month_year_of_manufacture","best_before","fssai_license"],
    "FOOD": ["product_name","net_quantity","manufacturer_name","manufacturer_address",
             "country_of_origin","mrp","month_year_of_manufacture","best_before",
             "fssai_license","ingredients","nutritional_info","allergen_info"],
    "COSMETICS": ["product_name","net_quantity","manufacturer_name","manufacturer_address",
                  "country_of_origin","mrp","month_year_of_manufacture","best_before","ingredients"],
    "ELECTRONICS": ["product_name","manufacturer_name","manufacturer_address","country_of_origin",
                    "mrp","month_year_of_manufacture","bis_license","customer_care"],
    "MEDICINE": ["product_name","net_quantity","manufacturer_name","manufacturer_address",
                 "country_of_origin","mrp","month_year_of_manufacture","best_before",
                 "batch_number","drug_license","composition"],
}

DEMO_COMPLIANT = {
    "product_name": {"value": "Sunrise Whole Wheat Flour", "confidence": 0.97},
    "net_quantity": {"value": "1 Kg (Net)", "confidence": 0.94},
    "manufacturer_name": {"value": "Sunrise Foods Pvt. Ltd.", "confidence": 0.96},
    "manufacturer_address": {"value": "45, Industrial Area, Pune - 411001, Maharashtra", "confidence": 0.91},
    "country_of_origin": {"value": "India", "confidence": 0.99},
    "mrp": {"value": "MRP: Rs. 55.00 (Incl. of all taxes)", "confidence": 0.98},
    "month_year_of_manufacture": {"value": "Aug 2025", "confidence": 0.93},
    "best_before": {"value": "12 months from manufacture", "confidence": 0.92},
    "fssai_license": {"value": "10013022000100", "confidence": 0.95},
    "ingredients": {"value": "Whole Wheat Flour (100%)", "confidence": 0.97},
    "nutritional_info": {"value": "Energy 340 kcal, Protein 12g, Fat 1.5g per 100g", "confidence": 0.90},
    "allergen_info": {"value": "Contains Gluten", "confidence": 0.96},
}

DEMO_MISSING = {
    "product_name": {"value": "Tasty Biscuits", "confidence": 0.88},
    "net_quantity": {"value": "200g", "confidence": 0.85},
    "manufacturer_name": {"value": None, "confidence": 0.0},
    "manufacturer_address": {"value": None, "confidence": 0.0},
    "country_of_origin": {"value": "India", "confidence": 0.91},
    "mrp": {"value": "Rs. 30", "confidence": 0.72},
    "month_year_of_manufacture": {"value": None, "confidence": 0.0},
    "best_before": {"value": "6 months", "confidence": 0.80},
    "fssai_license": {"value": "1001", "confidence": 0.60},
    "ingredients": {"value": "Flour, Sugar, Vegetable Oil", "confidence": 0.82},
    "nutritional_info": {"value": None, "confidence": 0.0},
    "allergen_info": {"value": None, "confidence": 0.0},
}

DEMO_MULTIPLE = {
    "product_name": {"value": "QuickSnack Chips", "confidence": 0.55},
    "net_quantity": {"value": "100 grams", "confidence": 0.78},
    "manufacturer_name": {"value": "XYZ Snacks", "confidence": 0.62},
    "manufacturer_address": {"value": None, "confidence": 0.0},
    "country_of_origin": {"value": None, "confidence": 0.0},
    "mrp": {"value": "MRP 25", "confidence": 0.65},
    "month_year_of_manufacture": {"value": "January 2024", "confidence": 0.50},
    "best_before": {"value": None, "confidence": 0.0},
    "fssai_license": {"value": "99887766554433", "confidence": 0.48},
    "ingredients": {"value": "Potato, Salt, Spices", "confidence": 0.70},
    "nutritional_info": {"value": None, "confidence": 0.0},
    "allergen_info": {"value": None, "confidence": 0.0},
}

def run_mock_pipeline(image_path: str, category: str = "FOOD", scenario: int = 0) -> dict[str, Any]:
    time.sleep(0.3)
    templates = [DEMO_COMPLIANT, DEMO_MISSING, DEMO_MULTIPLE]
    template = templates[scenario % 3]
    fields = REQUIRED_FIELDS.get(category, REQUIRED_FIELDS["GENERAL"])
    declarations = {}
    for field in fields:
        declarations[field] = template.get(field, {"value": None, "confidence": 0.0})
    return {
        "scenario": scenario,
        "category": category,
        "declarations": declarations,
        "processing_time_ms": 300,
        "ai_mode": "demo",
    }