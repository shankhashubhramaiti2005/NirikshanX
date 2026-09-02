import pytest
import numpy as np
import cv2
from app.ai.product_detection_service import ProductDetectionService

@pytest.fixture
def detector():
    return ProductDetectionService()

def test_detect_blank_image(detector, tmp_path):
    img_path = str(tmp_path / "blank.jpg")
    blank = np.zeros((300, 300, 3), dtype=np.uint8)
    cv2.imwrite(img_path, blank)

    res = detector.detect_product(img_path)
    assert res["is_packaged_product"] is False
    assert "blank" in res["reason"].lower() or "texture" in res["reason"].lower()

def test_detect_valid_product(detector, tmp_path):
    img_path = str(tmp_path / "product.jpg")
    img = np.zeros((400, 400, 3), dtype=np.uint8)
    cv2.rectangle(img, (50, 50), (350, 350), (255, 255, 255), -1)
    cv2.putText(img, "Product Label", (70, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.imwrite(img_path, img)

    res = detector.detect_product(img_path)
    assert res["is_packaged_product"] is True
    assert res["bounding_box"] is not None
