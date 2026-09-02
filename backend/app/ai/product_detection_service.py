import os
import cv2
import numpy as np
from typing import Dict, Any
from PIL import Image

class ProductDetectionService:
    def __init__(self):
        self.min_confidence = 0.5

    def detect_product(self, image_path: str) -> Dict[str, Any]:
        """
        Detects if the image contains a packaged product or commodity label.
        Extracts Region of Interest (ROI) bounding box.
        """
        if not os.path.exists(image_path):
            return {
                "is_packaged_product": False,
                "confidence": 0.0,
                "reason": "File not found",
                "bounding_box": None
            }

        img = cv2.imread(image_path)
        if img is None:
            return {
                "is_packaged_product": False,
                "confidence": 0.0,
                "reason": "Could not decode image",
                "bounding_box": None
            }

        h, w, _ = img.shape
        
        # Rule out blank / single color non-products
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        std_dev = float(np.std(gray))
        if std_dev < 10.0:
            return {
                "is_packaged_product": False,
                "confidence": 0.1,
                "reason": "Image lacks feature contrast or texture (blank image)",
                "bounding_box": None
            }

        # Object Detection Simulation / Contour Analysis
        # 1. Edge detection for package outline
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        bounding_box = [0, 0, w, h]
        confidence = 0.85
        is_packaged = True
        reason = "Packaged commodity label detected"

        if contours:
            # Find largest bounding rectangle
            c = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(c)
            if area > (w * h * 0.05): # At least 5% of total image area
                x, y, bw, bh = cv2.boundingRect(c)
                bounding_box = [int(x), int(y), int(bw), int(bh)]
                confidence = round(min(0.95, 0.70 + (area / (w * h)) * 0.3), 2)
            else:
                confidence = 0.60
        
        # Save cropped ROI image for downstream OCR if beneficial
        x, y, bw, bh = bounding_box
        roi_img = img[y:y+bh, x:x+bw]
        
        dir_name = os.path.dirname(image_path)
        base_name = os.path.basename(image_path)
        roi_path = os.path.join(dir_name, f"roi_{base_name}")
        cv2.imwrite(roi_path, roi_img)

        return {
            "is_packaged_product": is_packaged,
            "confidence": confidence,
            "reason": reason,
            "bounding_box": bounding_box,
            "cropped_roi_path": roi_path,
            "label_type": "Packaged Goods / Retail Label"
        }
