import pytest
import numpy as np
import cv2
from app.ai.pipeline import ImageValidationPipeline

@pytest.fixture
def pipeline():
    return ImageValidationPipeline()

def test_full_pipeline_flow(pipeline, tmp_path):
    # Generate sharp image with full label details
    img_path = str(tmp_path / "valid_label.jpg")
    img = np.full((500, 500, 3), 240, dtype=np.uint8)
    
    cv2.putText(img, "MRP Rs 350.00", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(img, "NET QTY: 500g", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(img, "MFD: 02/2026", (30, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(img, "EXP: 02/2027", (30, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(img, "Country of Origin: India", (30, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(img, "Customer Care: 1800-111-222", (30, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    cv2.imwrite(img_path, img)

    res = pipeline.process_image(img_path)
    assert "quality_metrics" in res
    assert "ocr_metrics" in res
    assert res["quality_metrics"]["is_acceptable"] is True
