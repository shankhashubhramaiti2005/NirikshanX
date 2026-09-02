import os
import time
import logging
from typing import Dict, Any, List
from .quality_service import QualityService
from .product_detection_service import ProductDetectionService
from .ocr_service import OCRService
from ..rules.engine import LegalMetrologyRulesEngine

logger = logging.getLogger(__name__)

class ImageValidationPipeline:
    def __init__(self):
        self.quality_service = QualityService()
        self.product_service = ProductDetectionService()
        self.ocr_service = OCRService()
        self.rules_engine = LegalMetrologyRulesEngine()

    def process_image(self, image_path: str, category: str = "general") -> Dict[str, Any]:
        """
        Full 4-Step Pipeline:
        1. Image Quality Assessment (Blur, Brightness, Resolution)
        2. Product Detection & ROI Extraction
        3. OCR & Text Preprocessing
        4. Legal Metrology Rules Compliance Verification
        """
        start_time = time.time()
        
        # Step 1: Quality Assessment
        quality_res = self.quality_service.assess_quality(image_path)
        
        # Early rejection if image quality is severely degraded
        if not quality_res.get("is_acceptable", False):
            processing_time = round(time.time() - start_time, 3)
            return {
                "status": "REJECTED",
                "stage_failed": "QUALITY_CHECK",
                "is_valid": False,
                "reasons": [f"Quality Error: {quality_res.get('issue', 'Image quality below threshold')}"],
                "quality_metrics": quality_res,
                "product_metrics": {},
                "ocr_metrics": {},
                "compliance_result": {},
                "processing_time_seconds": processing_time
            }

        # Step 2: Product & Object Detection
        product_res = self.product_service.detect_product(image_path)
        
        if not product_res.get("is_packaged_product", False):
            processing_time = round(time.time() - start_time, 3)
            return {
                "status": "REJECTED",
                "stage_failed": "OBJECT_DETECTION",
                "is_valid": False,
                "reasons": [f"Product Error: {product_res.get('reason', 'No packaged commodity detected in image')}"],
                "quality_metrics": quality_res,
                "product_metrics": product_res,
                "ocr_metrics": {},
                "compliance_result": {},
                "processing_time_seconds": processing_time
            }

        # Use cropped ROI for OCR if available
        target_ocr_path = product_res.get("cropped_roi_path", image_path)
        if not os.path.exists(target_ocr_path):
            target_ocr_path = image_path

        # Step 3: OCR Text Extraction
        ocr_res = self.ocr_service.extract_text(target_ocr_path)

        # Step 4: Legal Metrology Rules Compliance
        declarations = ocr_res.get("declarations", {})
        raw_text = ocr_res.get("cleaned_text", "")
        compliance_res = self.rules_engine.evaluate_compliance(declarations, raw_text, category=category)

        is_valid = compliance_res.get("is_compliant", False)
        reasons = []
        if not is_valid:
            for violation in compliance_res.get("violations", []):
                reasons.append(f"Non-Compliance [{violation.get('severity', 'HIGH')}]: {violation.get('description')}")

        processing_time = round(time.time() - start_time, 3)

        return {
            "status": "PASSED" if is_valid else "NON_COMPLIANT",
            "stage_failed": None if is_valid else "RULES_ENGINE",
            "is_valid": is_valid,
            "reasons": reasons,
            "quality_metrics": quality_res,
            "product_metrics": product_res,
            "ocr_metrics": ocr_res,
            "compliance_result": compliance_res,
            "processing_time_seconds": processing_time
        }
