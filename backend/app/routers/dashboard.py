from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models.scan import Scan
from ..models.violation import Violation

router = APIRouter()

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_scans = db.query(func.count(Scan.id)).scalar() or 0
    passed_scans = db.query(func.count(Scan.id)).filter(Scan.is_valid == True).scalar() or 0
    failed_scans = total_scans - passed_scans
    compliance_rate = round((passed_scans / total_scans * 100), 2) if total_scans > 0 else 100.0

    recent_scans = db.query(Scan).order_by(Scan.created_at.desc()).limit(10).all()

    return {
        "total_scans": total_scans,
        "passed_scans": passed_scans,
        "failed_scans": failed_scans,
        "compliance_rate_percentage": compliance_rate,
        "recent_scans": [
            {
                "id": s.id,
                "filename": s.image_filename,
                "is_valid": s.is_valid,
                "status": s.status,
                "processing_time": s.processing_time_seconds,
                "created_at": s.created_at.isoformat() if s.created_at else None
            } for s in recent_scans
        ]
    }
