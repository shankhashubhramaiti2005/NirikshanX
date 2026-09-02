import unittest
import os
import tempfile
from PIL import Image, ImageDraw

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.services.product_detection_service import ProductDetectionService, PRODUCT_DETECTION_THRESHOLD

class TestProductDetection(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_person_photo(self):
        img_path = os.path.join(self.temp_dir.name, "person.jpg")
        img = Image.new("RGB", (300, 300), color=(220, 160, 130)) # skin tone shade
        draw = ImageDraw.Draw(img)
        for i in range(10, 290, 10):
            draw.line([(i, 0), (i, 300)], fill=(200, 140, 110), width=1)
        img.save(img_path)

        res = ProductDetectionService.detect_product(img_path, threshold=PRODUCT_DETECTION_THRESHOLD)
        self.assertFalse(res["is_product_detected"])

    def test_landscape_photo(self):
        img_path = os.path.join(self.temp_dir.name, "landscape.jpg")
        img = Image.new("RGB", (300, 300), color=(50, 180, 50)) # green grass/vegetation
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 300, 150], fill=(20, 160, 240))
        for i in range(10, 290, 15):
            draw.line([(i, 150), (i, 300)], fill=(10, 120, 30), width=2)
        img.save(img_path)

        res = ProductDetectionService.detect_product(img_path, threshold=PRODUCT_DETECTION_THRESHOLD)
        self.assertFalse(res["is_product_detected"])

    def test_document_scan(self):
        img_path = os.path.join(self.temp_dir.name, "doc.jpg")
        img = Image.new("RGB", (300, 300), color=(245, 245, 245)) # plain white paper
        img.save(img_path)

        res = ProductDetectionService.detect_product(img_path, threshold=PRODUCT_DETECTION_THRESHOLD)
        self.assertFalse(res["is_product_detected"])

    def test_packaged_product(self):
        img_path = os.path.join(self.temp_dir.name, "product.jpg")
        img = Image.new("RGB", (400, 400), color=(180, 30, 30)) # red packaged box
        draw = ImageDraw.Draw(img)
        for cx in range(10, 390, 30):
            for cy in range(10, 390, 30):
                draw.rectangle([cx, cy, cx+20, cy+20], fill=(255, 215, 0)) # gold design squares
        img.save(img_path)

        res = ProductDetectionService.detect_product(img_path, threshold=PRODUCT_DETECTION_THRESHOLD)
        self.assertTrue(res["is_product_detected"])
        self.assertGreaterEqual(res["product_confidence"], PRODUCT_DETECTION_THRESHOLD)

if __name__ == "__main__":
    unittest.main()
