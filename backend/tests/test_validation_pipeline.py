import os
import pytest
from PIL import Image, ImageDraw, ImageFilter
from app.ai.pipeline import run_validation_pipeline
from app.ai.quality_service import check_image_quality
from app.ai.product_detection_service import ProductDetectionService, PRODUCT_DETECTION_THRESHOLD

TEST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_images"))

@pytest.fixture(scope="session", autouse=True)
def setup_test_images():
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
    # Add high-contrast declaration panel blocks
    draw_p.rectangle([50, 50, 350, 120], fill=(220, 50, 50))  # Brand header
    for y in range(140, 350, 12):
        draw_p.line([(60, y), (340, y)], fill=(10, 10, 10), width=3)
    img_prod.save(os.path.join(TEST_DIR, "product.jpg"))

    # 6. Blurry product image
    img_blur = img_prod.filter(ImageFilter.GaussianBlur(radius=8))
    img_blur.save(os.path.join(TEST_DIR, "product_blurry.jpg"))


def test_random_landscape_image():
    path = os.path.join(TEST_DIR, "landscape.jpg")
    res = run_validation_pipeline(path, category="FOOD")
    assert res["overall_status"] in ["NOT_A_PRODUCT", "REVIEW_REQUIRED"]
    assert res["overall_status"] != "PASS"
    assert res["overall_status"] != "COMPLIANT"


def test_photo_of_a_person():
    path = os.path.join(TEST_DIR, "person.jpg")
    res = run_validation_pipeline(path, category="FOOD")
    assert res["overall_status"] in ["NOT_A_PRODUCT", "REVIEW_REQUIRED"]
    assert res["overall_status"] != "PASS"
    assert res["overall_status"] != "COMPLIANT"


def test_blank_image():
    path = os.path.join(TEST_DIR, "blank.jpg")
    res = run_validation_pipeline(path, category="FOOD")
    assert res["overall_status"] in ["IMAGE_QUALITY_INSUFFICIENT", "REVIEW_REQUIRED", "NOT_A_PRODUCT"]
    assert res["overall_status"] != "PASS"
    assert res["overall_status"] != "COMPLIANT"


def test_random_text_document():
    path = os.path.join(TEST_DIR, "document.jpg")
    res = run_validation_pipeline(path, category="FOOD")
    assert res["overall_status"] in ["NOT_A_PRODUCT", "REVIEW_REQUIRED"]
    assert res["overall_status"] != "PASS"
    assert res["overall_status"] != "COMPLIANT"


def test_clear_packaged_commodity_image():
    path = os.path.join(TEST_DIR, "product.jpg")
    det = ProductDetectionService.detect_product(path)
    assert det["is_product_detected"] == True
    assert det["product_confidence"] >= PRODUCT_DETECTION_THRESHOLD


def test_blurry_product_image():
    path = os.path.join(TEST_DIR, "product_blurry.jpg")
    res = run_validation_pipeline(path, category="FOOD")
    assert res["overall_status"] in ["IMAGE_QUALITY_INSUFFICIENT", "REVIEW_REQUIRED"]
    assert res["overall_status"] != "PASS"


def test_demo_scenario_explicit():
    path = os.path.join(TEST_DIR, "product.jpg")
    res = run_validation_pipeline(path, category="FOOD", scenario=1)
    assert res["overall_status"] in ["PASS", "FAIL", "WARNING", "REVIEW_REQUIRED"]
