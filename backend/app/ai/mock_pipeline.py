import os
import time
from typing import Dict, Any
from .quality_service import QualityService
from .product_detection_service import ProductDetectionService
from .ocr_service import OCRService

class MockValidationPipeline:
    def __init__(self):
        self.quality_service = QualityService()
        self.product_service = ProductDetectionService()
        self.ocr_service = OCRService()

    def process_image(self, image_path: str) -> Dict[str, Any]:
        start_time = time.time()
        
        # 1. Quality Check
        quality_res = self.quality_service.assess_quality(image_path)
        
        # 2. Product Detection
        product_res = self.product_service.detect_product(image_path)
        
        # 3. OCR Analysis
        ocr_res = self.ocr_service.extract_text(image_path)
        
        # Determine overall validity
        is_valid = (
            quality_res.get("is_acceptable", False) and 
            product_res.get("is_packaged_product", False) and 
            len(ocr_res.get("raw_text", "").strip()) > 0
        )
        
        reasons = []
        if not quality_res.get("is_acceptable", False):
            reasons.append(f"Quality Issue: {quality_res.get('issue', 'Unacceptable image quality')}")
        if not product_res.get("is_packaged_product", False):
            reasons.append(f"Object Issue: {product_res.get('reason', 'No packaged commodity detected')}")
        if len(ocr_res.get("raw_text", "").strip()) == 0:
            reasons.append("OCR Issue: No legible text extracted from image")
            
        processing_time = round(time.time() - start_time, 3)
        
        return {
            "is_valid": is_valid,
            "reasons": reasons,
            "quality_metrics": quality_res,
            "product_metrics": product_res,
            "ocr_metrics": ocr_res,
            "processing_time_seconds": processing_time
        }
