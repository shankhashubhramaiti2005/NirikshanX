import pytest
import numpy as np
import cv2
from app.ai.quality_service import QualityService

@pytest.fixture
def quality():
    return QualityService(blur_threshold=100.0)

def test_sharp_image(quality, tmp_path):
    img_path = str(tmp_path / "sharp.jpg")
    # High contrast checkerboard pattern
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    img[::20, :] = 255
    cv2.imwrite(img_path, img)

    res = quality.assess_quality(img_path)
    assert res["is_acceptable"] is True
    assert res["blur_score"] > 100.0

def test_blurry_image(quality, tmp_path):
    img_path = str(tmp_path / "blurry.jpg")
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    img[::20, :] = 255
    # Heavy Gaussian Blur
    blurry = cv2.GaussianBlur(img, (25, 25), 0)
    cv2.imwrite(img_path, blurry)

    res = quality.assess_quality(img_path)
    assert res["is_acceptable"] is False
    assert "blurry" in res["issue"].lower()
