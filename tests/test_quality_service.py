import unittest
import os
import tempfile
from PIL import Image, ImageDraw

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.services.quality_service import check_image_quality

class TestQualityService(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_sharp_image(self):
        img_path = os.path.join(self.temp_dir.name, "sharp.jpg")
        img = Image.new("RGB", (400, 400), color=(120, 150, 180))
        draw = ImageDraw.Draw(img)
        # Add high-contrast lines for edge variance
        for i in range(10, 390, 5):
            draw.line([(i, 0), (i, 400)], fill=(0, 0, 0) if i % 10 == 0 else (255, 255, 255), width=2)
        img.save(img_path)

        res = check_image_quality(img_path)
        self.assertTrue(res["is_usable"])
        self.assertGreaterEqual(res["quality_score"], 0.50)

    def test_blurry_image(self):
        img_path = os.path.join(self.temp_dir.name, "blurry.jpg")
        img = Image.new("RGB", (300, 300), color=(128, 128, 128))
        img.save(img_path)

        res = check_image_quality(img_path)
        self.assertFalse(res["is_usable"])

    def test_pure_white_image(self):
        img_path = os.path.join(self.temp_dir.name, "white.jpg")
        img = Image.new("RGB", (300, 300), color=(255, 255, 255))
        img.save(img_path)

        res = check_image_quality(img_path)
        self.assertFalse(res["is_usable"])

    def test_pure_black_image(self):
        img_path = os.path.join(self.temp_dir.name, "black.jpg")
        img = Image.new("RGB", (300, 300), color=(0, 0, 0))
        img.save(img_path)

        res = check_image_quality(img_path)
        self.assertFalse(res["is_usable"])
        self.assertIn("dark", res["reason"].lower())

if __name__ == "__main__":
    unittest.main()
