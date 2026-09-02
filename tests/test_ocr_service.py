import pytest
from app.ai.ocr_service import OCRService

@pytest.fixture
def ocr():
    return OCRService()

def test_parse_declarations(ocr):
    sample_text = """
    MAX RETAIL PRICE Rs. 499.00 INCL. OF ALL TAXES
    NET QTY: 1.5 KG
    MFD DATE: 05/2026
    EXPIRY DATE: 05/2028
    COUNTRY OF ORIGIN: INDIA
    CONSUMER CARE: care@brand.in
    """
    declarations = ocr.parse_declarations(sample_text)
    assert declarations["mrp"] == "499.00"
    assert "1.5 KG" in declarations["net_quantity"]
    assert declarations["mfd_date"] == "05/2026"
    assert declarations["country_of_origin"].lower() == "india"

def test_post_processing_corrections(ocr):
    noisy = "MRP RS. 1O0.00 INCL TAXES"
    cleaned = ocr.post_process_text(noisy)
    assert "100.00" in cleaned
