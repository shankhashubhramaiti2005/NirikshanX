import os
import pytest
from app.ai.pipeline import ImageValidationPipeline

@pytest.fixture
def pipeline():
    return ImageValidationPipeline()

def test_pipeline_non_existent_file(pipeline):
    res = pipeline.process_image("non_existent_image_123.jpg")
    assert res["is_valid"] is False
    assert res["status"] == "REJECTED"
    assert "QUALITY_CHECK" in res["stage_failed"]

def test_pipeline_mock_product(pipeline, tmp_path):
    import cv2
    import numpy as np

    # Create dummy synthetic image
    img_path = str(tmp_path / "synthetic_product.jpg")
    img = np.zeros((400, 400, 3), dtype=np.uint8)
    # Add text and contrast
    cv2.putText(img, "MRP Rs 150.00 Net Wt: 200g", (20, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.imwrite(img_path, img)

    res = pipeline.process_image(img_path)
    assert "quality_metrics" in res
    assert "product_metrics" in res
    assert "ocr_metrics" in res
