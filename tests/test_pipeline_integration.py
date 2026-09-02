import unittest
import os
import tempfile
from PIL import Image, ImageDraw

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.pipeline import run_validation_pipeline

class TestPipelineIntegration(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_blurry_photo_pipeline(self):
        img_path = os.path.join(self.temp_dir.name, "blurry.jpg")
        img = Image.new("RGB", (300, 300), color=(128, 128, 128))
        img.save(img_path)

        res = run_validation_pipeline(img_path)
        self.assertEqual(res["overall_status"], "IMAGE_QUALITY_INSUFFICIENT")

    def test_person_photo_pipeline(self):
        img_path = os.path.join(self.temp_dir.name, "person.jpg")
        img = Image.new("RGB", (300, 300), color=(220, 160, 130)) # skin tone shade
        draw = ImageDraw.Draw(img)
        # Add high-contrast lines so Quality check passes but Product Detection fails
        for i in range(10, 290, 5):
            draw.line([(i, 0), (i, 300)], fill=(180, 120, 90), width=3)
        img.save(img_path)

        res = run_validation_pipeline(img_path)
        self.assertEqual(res["overall_status"], "NOT_A_PRODUCT")

    def test_landscape_photo_pipeline(self):
        img_path = os.path.join(self.temp_dir.name, "landscape.jpg")
        img = Image.new("RGB", (300, 300), color=(50, 180, 50)) # grass green
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 300, 150], fill=(20, 160, 240))
        for i in range(10, 290, 15):
            draw.line([(i, 150), (i, 300)], fill=(10, 120, 30), width=2)
        img.save(img_path)

        res = run_validation_pipeline(img_path)
        self.assertEqual(res["overall_status"], "NOT_A_PRODUCT")

    def test_packaged_commodity_pipeline(self):
        img_path = os.path.join(self.temp_dir.name, "product.jpg")
        img = Image.new("RGB", (400, 400), color=(180, 30, 30)) # red packaged box
        draw = ImageDraw.Draw(img)
        for cx in range(10, 390, 30):
            for cy in range(10, 390, 30):
                draw.rectangle([cx, cy, cx+20, cy+20], fill=(255, 215, 0)) # gold design squares
        img.save(img_path)

        res = run_validation_pipeline(img_path)
        # Should proceed past quality and product detection stage
        self.assertIn(res["overall_status"], ["REVIEW_REQUIRED", "PASS", "FAIL", "WARNING"])
        self.assertIn("ai_debug_metrics", res)
        self.assertGreater(res["ai_debug_metrics"]["product_confidence"], 0.60)

if __name__ == "__main__":
    unittest.main()
