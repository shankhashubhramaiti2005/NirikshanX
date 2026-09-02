from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.scan import Scan
from ..reports.pdf_generator import generate_scan_pdf_report

router = APIRouter()

@router.get("/pdf/{scan_id}")
def download_pdf_report(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    scan_data = {
        "id": scan.id,
        "status": scan.status,
        "is_valid": scan.is_valid,
        "processing_time_seconds": scan.processing_time_seconds,
        "compliance_result": scan.compliance_result or {}
    }

    pdf_bytes = generate_scan_pdf_report(scan_data)
    headers = {
        "Content-Disposition": f"attachment; filename=nirikshanx_report_scan_{scan_id}.pdf"
    }
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)
