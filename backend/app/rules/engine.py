import re
from typing import Dict, Any, List

class LegalMetrologyRulesEngine:
    def __init__(self):
        # Mandatory legal metrology declaration fields
        self.mandatory_fields = [
            {"field": "mrp", "name": "Maximum Retail Price (MRP)", "severity": "HIGH"},
            {"field": "net_quantity", "name": "Net Quantity / Weight", "severity": "HIGH"},
            {"field": "mfd_date", "name": "Date of Manufacture / Packing", "severity": "MEDIUM"},
            {"field": "country_of_origin", "name": "Country of Origin", "severity": "HIGH"},
            {"field": "customer_care", "name": "Consumer Care Helpline / Address", "severity": "MEDIUM"},
        ]

    def evaluate_compliance(self, declarations: Dict[str, Any], raw_text: str, category: str = "general") -> Dict[str, Any]:
        """
        Evaluates extracted declarations against Legal Metrology Rules (Packaged Commodities), 2011 / 2022 amendments.
        """
        violations = []
        passed_rules = []

        # 1. Mandatory Field Checks
        for req in self.mandatory_fields:
            field_key = req["field"]
            field_name = req["name"]
            severity = req["severity"]
            val = declarations.get(field_key)

            if not val or str(val).strip() == "":
                # Fallback scan in raw text if regex missed structured parsing
                if self._check_text_fallback(field_key, raw_text):
                    passed_rules.append(f"LM_REQ_{field_key.upper()}")
                else:
                    violations.append({
                        "rule_id": f"LM_REQ_{field_key.upper()}",
                        "field_name": field_name,
                        "severity": severity,
                        "description": f"Mandatory declaration missing: '{field_name}' not found on product label."
                    })
            else:
                passed_rules.append(f"LM_REQ_{field_key.upper()}")

        # 2. Specific Validation Rules
        # Rule: MRP formatting (must state 'incl. of all taxes' or numerical price)
        mrp_val = declarations.get("mrp")
        if mrp_val:
            if not re.search(r'[\d\.]+', mrp_val):
                violations.append({
                    "rule_id": "LM_MRP_FORMAT",
                    "field_name": "Maximum Retail Price (MRP)",
                    "severity": "HIGH",
                    "description": f"MRP value '{mrp_val}' does not contain a valid numerical currency amount."
                })

        # Rule: Expiry / Best before rule for perishable categories
        if category in ["food", "beverages", "pharma"]:
            exp_val = declarations.get("expiry_date")
            if not exp_val and not re.search(r'(?i)(best\s*before|use\s*by|exp)', raw_text):
                violations.append({
                    "rule_id": "LM_EXPIRY_MANDATORY",
                    "field_name": "Expiry / Best Before Date",
                    "severity": "HIGH",
                    "description": f"Expiry or Best Before date is mandatory for package category '{category}'."
                })

        is_compliant = len(violations) == 0

        return {
            "is_compliant": is_compliant,
            "total_rules_checked": len(self.mandatory_fields) + 1,
            "violations_count": len(violations),
            "violations": violations,
            "passed_rules": passed_rules,
            "compliance_score_percentage": round(max(0.0, (1 - len(violations)/6) * 100), 2)
        }

    def _check_text_fallback(self, field_key: str, text: str) -> bool:
        if not text:
            return False
        text_lower = text.lower()
        if field_key == "mrp" and any(k in text_lower for k in ["mrp", "rs.", "price"]):
            return True
        if field_key == "net_quantity" and any(k in text_lower for k in ["net wt", "net qty", "g", "kg", "ml", "l"]):
            return True
        if field_key == "mfd_date" and any(k in text_lower for k in ["mfd", "mfg", "packed", "pkd"]):
            return True
        if field_key == "country_of_origin" and any(k in text_lower for k in ["india", "origin", "made in"]):
            return True
        if field_key == "customer_care" and any(k in text_lower for k in ["care", "helpline", "email", "consumer"]):
            return True
        return False
