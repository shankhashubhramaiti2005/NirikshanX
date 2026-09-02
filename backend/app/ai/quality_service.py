import os
import cv2
import numpy as np
from typing import Dict, Any

class QualityService:
    def __init__(self, blur_threshold: float = 100.0, min_resolution: int = 200):
        self.blur_threshold = blur_threshold
        self.min_resolution = min_resolution

    def calculate_blur_variance(self, image: np.ndarray) -> float:
        """Calculates Laplacian variance to determine blurriness."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return float(cv2.Laplacian(gray, cv2.CV_64F).var())

    def calculate_brightness(self, image: np.ndarray) -> float:
        """Calculates average HSV V-channel brightness (0-255)."""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        return float(np.mean(hsv[:, :, 2]))

    def assess_quality(self, image_path: str) -> Dict[str, Any]:
        """
        Assesses image quality: Blur, Brightness, Contrast, Resolution.
        Returns pass/fail status with metrics.
        """
        if not os.path.exists(image_path):
            return {
                "is_acceptable": False,
                "issue": "File not found",
                "blur_score": 0.0,
                "brightness": 0.0,
                "resolution": [0, 0]
            }

        img = cv2.imread(image_path)
        if img is None:
            return {
                "is_acceptable": False,
                "issue": "Unable to load image file",
                "blur_score": 0.0,
                "brightness": 0.0,
                "resolution": [0, 0]
            }

        h, w, _ = img.shape

        # 1. Resolution Check
        if h < self.min_resolution or w < self.min_resolution:
            return {
                "is_acceptable": False,
                "issue": f"Resolution too low ({w}x{h}). Minimum required: {self.min_resolution}x{self.min_resolution}",
                "blur_score": 0.0,
                "brightness": 0.0,
                "resolution": [w, h]
            }

        # 2. Blur Check
        blur_score = self.calculate_blur_variance(img)
        is_blurry = blur_score < self.blur_threshold

        # 3. Brightness Check
        brightness = self.calculate_brightness(img)
        is_dark = brightness < 40.0
        is_overexposed = brightness > 225.0

        is_acceptable = True
        issues = []
        if is_blurry:
            is_acceptable = False
            issues.append(f"Image is too blurry (Blur variance: {round(blur_score, 1)} < {self.blur_threshold})")
        if is_dark:
            is_acceptable = False
            issues.append(f"Image is too dark (Brightness: {round(brightness, 1)} < 40.0)")
        if is_overexposed:
            is_acceptable = False
            issues.append(f"Image is overexposed (Brightness: {round(brightness, 1)} > 225.0)")

        return {
            "is_acceptable": is_acceptable,
            "issue": "; ".join(issues) if issues else None,
            "blur_score": round(blur_score, 2),
            "brightness": round(brightness, 2),
            "resolution": [w, h],
            "quality_grade": "A" if blur_score > 300 and 60 <= brightness <= 190 else ("B" if is_acceptable else "F")
        }
