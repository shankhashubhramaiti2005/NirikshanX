import os
from typing import Dict, Any
from .quality_service import check_image_quality
from .product_detection_service import ProductDetectionService, PRODUCT_DETECTION_THRESHOLD
from .ocr_service import OCRService
from .mock_pipeline import run_mock_pipeline, REQUIRED_FIELDS
from ..rules.engine import run_engine
from ..config import settings

def run_validation_pipeline(image_path: str, category: str = "FOOD", scenario: int = 0, product_name_hint: str = "") -> Dict[str, Any]:
    """
    Executes the multi-stage AI compliance inspection pipeline:
    1. Image Quality Validation
    2. Packaged Product / Commodity Detection
    3. Label & Text Region Detection
    4. OCR & Legal Metrology Declaration Extraction
    5. Rule Engine Evaluation & Real Confidence Score Calculation
    6. Final State Determination (PASS, FAIL, REVIEW_REQUIRED, NOT_A_PRODUCT, IMAGE_QUALITY_INSUFFICIENT)
    """

    # Check if demo mode is explicitly requested via scenario > 0
    if settings.DEMO_MODE and scenario > 0:
        mock_data = run_mock_pipeline(image_path, category, scenario)
        declarations = mock_data["declarations"]
        engine_res = run_engine(declarations, category)
        return {
            "overall_status": engine_res["overall_status"],
            "compliance_score": engine_res["compliance_score"],
            "declarations": declarations,
            "checks": engine_res["checks"],
            "ai_debug_metrics": {
                "quality_score": 0.95,
                "product_confidence": 0.96,
                "label_confidence": 0.94,
                "ocr_confidence": 0.92,
                "extraction_confidence": 0.90,
                "inspection_confidence": 0.93,
                "model_available": True,
                "demo_mode_active": True,
                "reason": f"Demo scenario {scenario} executed successfully."
            },
            "warnings": [],
            "messages": []
        }

    # ════════════════════════════════════════════════ STAGE 1: IMAGE QUALITY CHECK
    quality_res = check_image_quality(image_path)
    if not quality_res["is_usable"]:
        return {
            "overall_status": "IMAGE_QUALITY_INSUFFICIENT",
            "scan_status": "IMAGE_QUALITY_INSUFFICIENT",
            "compliance_score": None,
            "declarations": {},
            "checks": [],
            "warnings": [quality_res["reason"]] + quality_res.get("suggestions", []),
            "ai_debug_metrics": {
                "quality_score": quality_res["quality_score"],
                "product_confidence": 0.0,
                "label_confidence": 0.0,
                "ocr_confidence": 0.0,
                "extraction_confidence": 0.0,
                "inspection_confidence": quality_res["quality_score"],
                "model_available": True,
                "demo_mode_active": False,
                "reason": quality_res["reason"]
            }
        }

    # ════════════════════════════════════════════════ STAGE 2: PACKAGED PRODUCT DETECTION
    detection_res = ProductDetectionService.detect_product(image_path, threshold=PRODUCT_DETECTION_THRESHOLD)
    product_conf = detection_res["product_confidence"]

    if not detection_res["is_product_detected"]:
        return {
            "overall_status": "NOT_A_PRODUCT",
            "scan_status": "NOT_A_PRODUCT",
            "compliance_score": None,
            "declarations": {},
            "checks": [],
            "warnings": detection_res["warnings"],
            "ai_debug_metrics": {
                "quality_score": quality_res["quality_score"],
                "product_confidence": product_conf,
                "label_confidence": detection_res["label_confidence"],
                "ocr_confidence": 0.0,
                "extraction_confidence": 0.0,
                "inspection_confidence": product_conf,
                "model_available": detection_res["model_available"],
                "demo_mode_active": False,
                "reason": detection_res["reason"]
            }
        }

    # ════════════════════════════════════════════════ STAGE 3: OCR & DECLARATION EXTRACTION
    ocr_res = OCRService.extract_declarations(image_path, category=category)
    extracted_decls = ocr_res["declarations"]
    ocr_conf = ocr_res["ocr_confidence"]
    evidence_count = ocr_res["evidence_found"]

    # Fill mandatory fields with defaults if not present
    req_fields = REQUIRED_FIELDS.get(category, REQUIRED_FIELDS["GENERAL"])
    final_declarations: Dict[str, Any] = {}
    for f in req_fields:
        if f in extracted_decls and extracted_decls[f].get("value"):
            final_declarations[f] = extracted_decls[f]
        elif f == "product_name" and product_name_hint and str(product_name_hint).strip():
            final_declarations[f] = {"value": str(product_name_hint).strip(), "confidence": 0.85}
            evidence_count += 1
        else:
            final_declarations[f] = {"value": None, "confidence": 0.0}

    # ════════════════════════════════════════════════ STAGE 4: RULE ENGINE VALIDATION
    engine_res = run_engine(final_declarations, category)
    checks = engine_res["checks"]
    rule_score = engine_res["compliance_score"]

    # ════════════════════════════════════════════════ STAGE 5: REAL CONFIDENCE METRICS & DECISION
    extraction_conf = round(sum(d.get("confidence", 0.0) for d in final_declarations.values()) / max(len(req_fields), 1), 2)
    inspection_conf = round((quality_res["quality_score"] * 0.20) + (product_conf * 0.30) + (ocr_conf * 0.25) + (extraction_conf * 0.25), 2)

    # Prevent "No Violations = Compliant" Bug:
    # If positive evidence extracted is less than threshold (e.g. fewer than 2 mandatory fields), status must be REVIEW_REQUIRED (NEEDS_REVIEW)
    overall_st = engine_res["overall_status"]
    scan_st = "COMPLETED"

    if evidence_count < 2 or inspection_conf < 0.60:
        overall_st = "REVIEW_REQUIRED"
        scan_st = "REVIEW_REQUIRED"
        adjusted_score = round(min(rule_score, 45.0), 1)
    else:
        adjusted_score = rule_score

    warnings = ocr_res["warnings"]
    if overall_st == "REVIEW_REQUIRED":
        warnings.append("Insufficient declaration evidence extracted from product label - human review required.")

    return {
        "overall_status": overall_st,
        "scan_status": scan_st,
        "compliance_score": adjusted_score,
        "declarations": final_declarations,
        "checks": checks,
        "warnings": warnings,
        "ai_debug_metrics": {
            "quality_score": quality_res["quality_score"],
            "product_confidence": product_conf,
            "label_confidence": detection_res["label_confidence"],
            "ocr_confidence": ocr_conf,
            "extraction_confidence": extraction_conf,
            "inspection_confidence": inspection_conf,
            "model_available": detection_res["model_available"],
            "evidence_found": evidence_count,
            "demo_mode_active": False,
            "reason": detection_res["reason"]
        }
    }
