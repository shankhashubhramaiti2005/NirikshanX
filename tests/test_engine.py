import pytest
from app.rules.engine import LegalMetrologyRulesEngine

@pytest.fixture
def engine():
    return LegalMetrologyRulesEngine()

def test_full_declarations_pass(engine):
    declarations = {
        "mrp": "250.00",
        "net_quantity": "500g",
        "mfd_date": "01/2026",
        "expiry_date": "12/2026",
        "country_of_origin": "India",
        "customer_care": "1800-123-4567"
    }
    res = engine.evaluate_compliance(declarations, "MRP Rs 250 Net Wt 500g Packed 01/2026 Made in India Helpline 1800-123-4567")
    assert res["is_compliant"] is True
    assert len(res["violations"]) == 0

def test_missing_mrp_fails(engine):
    declarations = {
        "mrp": None,
        "net_quantity": "500g",
        "mfd_date": "01/2026",
        "expiry_date": "12/2026",
        "country_of_origin": "India",
        "customer_care": "1800-123-4567"
    }
    res = engine.evaluate_compliance(declarations, "Net Wt 500g Packed 01/2026 Made in India")
    assert res["is_compliant"] is False
    assert any(v["field_name"] == "Maximum Retail Price (MRP)" for v in res["violations"])
