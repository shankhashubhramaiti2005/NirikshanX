import os
import sys
import unittest
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ai.pipeline import run_validation_pipeline
from app.ai.quality_service import check_image_quality
from app.ai.product_detection_service import ProductDetectionService, PRODUCT_DETECTION_THRESHOLD

TEST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_images"))

class TestValidationPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.makedirs(TEST_DIR, exist_ok=True)
        
        # 1. Landscape image (Sky blue top half, vegetation green bottom half)
        img_landscape = Image.new("RGB", (400, 400), (135, 206, 235))
        draw = ImageDraw.Draw(img_landscape)
        draw.rectangle([0, 200, 400, 400], fill=(34, 139, 34))
        img_landscape.save(os.path.join(TEST_DIR, "landscape.jpg"))

        # 2. Person portrait image (Skin tone pixels block)
        img_person = Image.new("RGB", (400, 400), (220, 160, 120))
        img_person.save(os.path.join(TEST_DIR, "person.jpg"))

        # 3. Blank image (Solid white)
        img_blank = Image.new("RGB", (400, 400), (255, 255, 255))
        img_blank.save(os.path.join(TEST_DIR, "blank.jpg"))

        # 4. Document image (White background with horizontal text lines, no package box)
        img_doc = Image.new("RGB", (400, 400), (245, 245, 245))
        draw_doc = ImageDraw.Draw(img_doc)
        for y in range(30, 370, 15):
            draw_doc.line([(30, y), (370, y)], fill=(40, 40, 40), width=2)
        img_doc.save(os.path.join(TEST_DIR, "document.jpg"))

        # 5. Packaged Commodity Image (Simulated commercial package box with contrast declarations grid)
        img_prod = Image.new("RGB", (400, 400), (20, 30, 60))
        draw_p = ImageDraw.Draw(img_prod)
        draw_p.rectangle([30, 30, 370, 370], fill=(240, 240, 240), outline=(220, 50, 50), width=4)
        draw_p.rectangle([50, 50, 350, 120], fill=(220, 50, 50))
        for y in range(140, 350, 12):
            draw_p.line([(60, y), (340, y)], fill=(10, 10, 10), width=3)
        img_prod.save(os.path.join(TEST_DIR, "product.jpg"))

        # 6. Blurry product image
        img_blur = img_prod.filter(ImageFilter.GaussianBlur(radius=8))
        img_blur.save(os.path.join(TEST_DIR, "product_blurry.jpg"))

    def test_1_random_landscape_image(self):
        path = os.path.join(TEST_DIR, "landscape.jpg")
        res = run_validation_pipeline(path, category="FOOD")
        self.assertIn(res["overall_status"], ["NOT_A_PRODUCT", "REVIEW_REQUIRED", "IMAGE_QUALITY_INSUFFICIENT"])
        self.assertNotIn(res["overall_status"], ["PASS", "COMPLIANT"])
        print("[PASS] TEST 1 (Landscape Image) Passed: Status =", res["overall_status"])

    def test_2_photo_of_a_person(self):
        path = os.path.join(TEST_DIR, "person.jpg")
        res = run_validation_pipeline(path, category="FOOD")
        self.assertIn(res["overall_status"], ["NOT_A_PRODUCT", "REVIEW_REQUIRED", "IMAGE_QUALITY_INSUFFICIENT"])
        self.assertNotIn(res["overall_status"], ["PASS", "COMPLIANT"])
        print("[PASS] TEST 2 (Photo of Person) Passed: Status =", res["overall_status"])

    def test_3_blank_image(self):
        path = os.path.join(TEST_DIR, "blank.jpg")
        res = run_validation_pipeline(path, category="FOOD")
        self.assertIn(res["overall_status"], ["IMAGE_QUALITY_INSUFFICIENT", "REVIEW_REQUIRED", "NOT_A_PRODUCT"])
        self.assertNotIn(res["overall_status"], ["PASS", "COMPLIANT"])
        print("[PASS] TEST 3 (Blank Image) Passed: Status =", res["overall_status"])

    def test_4_random_text_document(self):
        path = os.path.join(TEST_DIR, "document.jpg")
        res = run_validation_pipeline(path, category="FOOD")
        self.assertIn(res["overall_status"], ["NOT_A_PRODUCT", "REVIEW_REQUIRED", "IMAGE_QUALITY_INSUFFICIENT"])
        self.assertNotIn(res["overall_status"], ["PASS", "COMPLIANT"])
        print("[PASS] TEST 4 (Random Text Document) Passed: Status =", res["overall_status"])

    def test_5_clear_packaged_commodity_image(self):
        path = os.path.join(TEST_DIR, "product.jpg")
        det = ProductDetectionService.detect_product(path)
        self.assertTrue(det["is_product_detected"])
        self.assertGreaterEqual(det["product_confidence"], PRODUCT_DETECTION_THRESHOLD)
        print("[PASS] TEST 5 (Packaged Commodity Image) Passed: Detection Confidence =", det["product_confidence"])

    def test_6_blurry_product_image(self):
        path = os.path.join(TEST_DIR, "product_blurry.jpg")
        res = run_validation_pipeline(path, category="FOOD")
        self.assertIn(res["overall_status"], ["IMAGE_QUALITY_INSUFFICIENT", "REVIEW_REQUIRED", "NOT_A_PRODUCT"])
        self.assertNotIn(res["overall_status"], ["PASS", "COMPLIANT"])
        print("[PASS] TEST 6 (Blurry Product Image) Passed: Status =", res["overall_status"])

    def test_7_demo_scenario_controlled(self):
        path = os.path.join(TEST_DIR, "product.jpg")
        res = run_validation_pipeline(path, category="FOOD", scenario=1)
        self.assertIn(res["overall_status"], ["PASS", "FAIL", "WARNING", "REVIEW_REQUIRED"])
        print("[PASS] TEST 7 (Explicit Demo Scenario) Passed: Status =", res["overall_status"])

if __name__ == "__main__":
    unittest.main()
