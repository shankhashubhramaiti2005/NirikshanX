import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.services.engine import run_engine

class TestEngine(unittest.TestCase):

    def test_complete_valid_declarations(self):
        declarations = {
            "product_name": {"value": "Dairy Milk", "confidence": 0.95},
            "net_quantity": {"value": "100g", "confidence": 0.90},
            "manufacturer_name": {"value": "Cadbury Pvt Ltd", "confidence": 0.90},
            "manufacturer_address": {"value": "Plot 5, Mumbai", "confidence": 0.88},
            "country_of_origin": {"value": "India", "confidence": 0.95},
            "mrp": {"value": "Rs. 50 (Incl. of all taxes)", "confidence": 0.95},
            "month_year_of_manufacture": {"value": "01/2026", "confidence": 0.90},
            "best_before": {"value": "12 months", "confidence": 0.90},
            "fssai_license": {"value": "10012022000123", "confidence": 0.95},
            "ingredients": {"value": "Sugar, Cocoa", "confidence": 0.90},
            "nutritional_info": {"value": "Energy 500 kcal", "confidence": 0.85},
            "allergen_info": {"value": "Milk", "confidence": 0.85},
        }

        res = run_engine(declarations, "FOOD")
        self.assertEqual(res["overall_status"], "PASS")
        self.assertEqual(res["compliance_score"], 100.0)

    def test_missing_mandatory_field(self):
        declarations = {
            "product_name": {"value": "Dairy Milk", "confidence": 0.95},
            # Missing manufacturer_name, mrp, etc.
        }

        res = run_engine(declarations, "FOOD")
        self.assertEqual(res["overall_status"], "FAIL")
        self.assertLess(res["compliance_score"], 50.0)
        
        failed_checks = [c for c in res["checks"] if c["status"] == "FAIL"]
        self.assertGreater(len(failed_checks), 0)

    def test_malformed_fssai_number(self):
        declarations = {
            "product_name": {"value": "Dairy Milk", "confidence": 0.95},
            "net_quantity": {"value": "100g", "confidence": 0.90},
            "manufacturer_name": {"value": "Cadbury Pvt Ltd", "confidence": 0.90},
            "manufacturer_address": {"value": "Plot 5, Mumbai", "confidence": 0.88},
            "country_of_origin": {"value": "India", "confidence": 0.95},
            "mrp": {"value": "Rs. 50", "confidence": 0.95},
            "month_year_of_manufacture": {"value": "01/2026", "confidence": 0.90},
            "best_before": {"value": "12 months", "confidence": 0.90},
            "fssai_license": {"value": "12345", "confidence": 0.95}, # invalid length (5 digits instead of 14)
            "ingredients": {"value": "Sugar, Cocoa", "confidence": 0.90},
            "nutritional_info": {"value": "Energy 500 kcal", "confidence": 0.85},
            "allergen_info": {"value": "Milk", "confidence": 0.85},
        }

        res = run_engine(declarations, "FOOD")
        fssai_check = next(c for c in res["checks"] if c["rule_id"] == "LM-FSSAI-FORMAT")
        self.assertEqual(fssai_check["status"], "FAIL")

if __name__ == "__main__":
    unittest.main()
