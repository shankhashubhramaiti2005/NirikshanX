import unittest
import os
import tempfile
from PIL import Image

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.services.ocr_service import OCRService

class TestOCRService(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_parse_fields_from_text(self):
        sample_text = """
        CADBURY DAIRY MILK CHOCOLATE
        NET QTY: 100 G
        MRP Rs. 50 (Incl. of all taxes)
        FSSAI LIC NO: 10012022000123
        MFD: 01/2026
        BEST BEFORE 12 MONTHS FROM MANUFACTURE
        MFG BY: CADBURY INDIA PVT LTD
        ADDRESS: PLOT 12, INDUSTRIAL AREA, MUMBAI
        COUNTRY OF ORIGIN: INDIA
        INGREDIENTS: SUGAR, MILK SOLIDS, COCOA BUTTER
        NUTRITIONAL INFO: ENERGY 530 KCAL, PROTEIN 7.5G
        ALLERGEN: CONTAINS MILK AND SOY
        BATCH NO: BATCH-998
        CUSTOMER CARE: 1800-22-1234
        """
        lines = [line.strip() for line in sample_text.splitlines() if line.strip()]
        fields = OCRService._parse_fields_from_text(sample_text, lines, "FOOD")

        self.assertIsNotNone(fields["product_name"]["value"])
        self.assertIn("CADBURY", fields["product_name"]["value"].upper())
        self.assertEqual(fields["net_quantity"]["value"], "100 G")
        self.assertIn("50", fields["mrp"]["value"])
        self.assertEqual(fields["fssai_license"]["value"], "10012022000123")
        self.assertEqual(fields["country_of_origin"]["value"], "India")
        self.assertIsNotNone(fields["month_year_of_manufacture"]["value"])
        self.assertIsNotNone(fields["best_before"]["value"])
        self.assertIsNotNone(fields["manufacturer_name"]["value"])
        self.assertIsNotNone(fields["ingredients"]["value"])
        self.assertIsNotNone(fields["batch_number"]["value"])
        self.assertIsNotNone(fields["customer_care"]["value"])

        # Field level confidence verify
        self.assertGreaterEqual(fields["fssai_license"]["confidence"], 0.90)

    def test_extract_declarations_empty_path(self):
        res = OCRService.extract_declarations("")
        self.assertEqual(res["ocr_confidence"], 0.0)
        self.assertEqual(res["evidence_found"], 0)

if __name__ == "__main__":
    unittest.main()
