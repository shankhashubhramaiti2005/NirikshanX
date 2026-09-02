import re
from typing import Any

CONFIDENCE_THRESHOLD = 0.65

REQUIRED_FIELDS = {
    "GENERAL": ["product_name","net_quantity","manufacturer_name","manufacturer_address",
                "country_of_origin","mrp","month_year_of_manufacture","best_before","fssai_license"],
    "FOOD": ["product_name","net_quantity","manufacturer_name","manufacturer_address",
             "country_of_origin","mrp","month_year_of_manufacture","best_before",
             "fssai_license","ingredients","nutritional_info","allergen_info"],
    "COSMETICS": ["product_name","net_quantity","manufacturer_name","manufacturer_address",
                  "country_of_origin","mrp","month_year_of_manufacture","best_before","ingredients"],
    "ELECTRONICS": ["product_name","manufacturer_name","manufacturer_address","country_of_origin",
                    "mrp","month_year_of_manufacture","bis_license","customer_care"],
    "MEDICINE": ["product_name","net_quantity","manufacturer_name","manufacturer_address",
                 "country_of_origin","mrp","month_year_of_manufacture","best_before",
                 "batch_number","drug_license","composition"],
}

FIELD_META = {
    "product_name": ("Name of commodity", "HIGH", "R-4(a)"),
    "net_quantity": ("Net quantity in standard units", "HIGH", "R-4(b)"),
    "manufacturer_name": ("Manufacturer name", "CRITICAL", "R-4(c)"),
    "manufacturer_address": ("Manufacturer address", "CRITICAL", "R-4(c)"),
    "country_of_origin": ("Country of origin", "MEDIUM", "R-4(d)"),
    "mrp": ("Maximum retail price", "CRITICAL", "R-4(e)"),
    "month_year_of_manufacture": ("Month and year of manufacture", "HIGH", "R-4(f)"),
    "best_before": ("Best before/expiry date", "HIGH", "R-4(g)"),
    "fssai_license": ("FSSAI license number (14 digits)", "HIGH", "FSS-Act"),
    "ingredients": ("List of ingredients", "HIGH", "R-4(h)"),
    "nutritional_info": ("Nutritional information per 100g", "MEDIUM", "R-4(i)"),
    "allergen_info": ("Allergen declaration", "MEDIUM", "R-4(j)"),
    "bis_license": ("BIS license number", "HIGH", "BIS-Act"),
    "customer_care": ("Customer care contact", "MEDIUM", "R-4(k)"),
    "batch_number": ("Batch/lot number", "HIGH", "R-4(l)"),
    "drug_license": ("Drug license number", "CRITICAL", "D&C-Act"),
    "composition": ("Active composition/ingredients", "HIGH", "R-4(m)"),
}

def _check_fssai(value: str) -> bool:
    return bool(value) and bool(re.fullmatch(r"\d{14}", value.strip()))

def _check_mrp(value: str) -> bool:
    if not value:
        return False
    v = value.upper()
    return any(x in v for x in ["MRP", "RS.", "RS ", "\u20b9"])

def run_engine(declarations: dict[str, Any], category: str) -> dict:
    required = REQUIRED_FIELDS.get(category, REQUIRED_FIELDS["GENERAL"])
    results = []
    pass_count = 0.0
    total = len(required)

    for field in required:
        info = declarations.get(field, {"value": None, "confidence": 0.0})
        value = info.get("value")
        confidence = float(info.get("confidence", 0.0))
        label, default_severity, rule_ref = FIELD_META.get(field, (field, "MEDIUM", "R-4"))

        if value is None or str(value).strip() == "":
            results.append({
                "rule_id": f"LM-{field.upper()}",
                "field": field,
                "status": "FAIL",
                "severity": default_severity,
                "message": f"Missing mandatory declaration: {label} [{rule_ref}]",
                "extracted_value": None,
                "confidence": 0.0,
                "evidence": {"rule_reference": rule_ref, "requirement": label},
            })
            continue

        if confidence < CONFIDENCE_THRESHOLD:
            results.append({
                "rule_id": f"LM-{field.upper()}",
                "field": field,
                "status": "REVIEW_REQUIRED",
                "severity": default_severity,
                "message": f"Low confidence ({confidence:.0%}) in extracted value for {label} - manual review required",
                "extracted_value": value,
                "confidence": confidence,
                "evidence": {"rule_reference": rule_ref, "extracted": value, "confidence": confidence},
            })
            pass_count += 0.5
            continue

        if field == "fssai_license" and not _check_fssai(value):
            results.append({
                "rule_id": f"LM-FSSAI-FORMAT",
                "field": field,
                "status": "FAIL",
                "severity": "HIGH",
                "message": f"FSSAI license must be exactly 14 digits. Extracted: \"{value}\"",
                "extracted_value": value,
                "confidence": confidence,
                "evidence": {"rule_reference": rule_ref, "extracted": value},
            })
            continue

        if field == "mrp" and not _check_mrp(value):
            results.append({
                "rule_id": f"LM-MRP-FORMAT",
                "field": field,
                "status": "WARNING",
                "severity": "MEDIUM",
                "message": f"MRP should display Rs./MRP symbol clearly. Extracted: \"{value}\"",
                "extracted_value": value,
                "confidence": confidence,
                "evidence": {"rule_reference": rule_ref, "extracted": value},
            })
            pass_count += 0.7
            continue

        results.append({
            "rule_id": f"LM-{field.upper()}",
            "field": field,
            "status": "PASS",
            "severity": "LOW",
            "message": f"{label}: Present and valid",
            "extracted_value": value,
            "confidence": confidence,
            "evidence": {"rule_reference": rule_ref, "extracted": value},
        })
        pass_count += 1.0

    score = round((pass_count / total) * 100, 1) if total > 0 else 0.0
    violations = [r for r in results if r["status"] != "PASS"]
    has_critical_fail = any(r["severity"] == "CRITICAL" and r["status"] == "FAIL" for r in results)
    has_any_review = any(r["status"] == "REVIEW_REQUIRED" for r in results)

    if has_critical_fail:
        overall = "FAIL"
    elif violations:
        overall = "REVIEW_REQUIRED" if has_any_review else "WARNING"
    else:
        overall = "PASS"

    return {
        "compliance_score": score,
        "overall_status": overall,
        "checks": results,
        "summary": {
            "total_checks": total,
            "passed": len([r for r in results if r["status"] == "PASS"]),
            "failed": len([r for r in results if r["status"] == "FAIL"]),
            "warnings": len([r for r in results if r["status"] == "WARNING"]),
            "review_required": len([r for r in results if r["status"] == "REVIEW_REQUIRED"]),
        }
    }