from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import Scan, Violation, ScanStatus, ViolationStatus, ViolationSeverity
from ..dependencies.auth import get_current_user
from ..models.user import User

router = APIRouter()

@router.get("/stats")
def get_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total = db.query(func.count(Scan.id)).scalar() or 0
    compliant = db.query(func.count(Scan.id)).filter(Scan.overall_status == ViolationStatus.PASS).scalar() or 0
    violations = db.query(func.count(Violation.id)).filter(Violation.status != ViolationStatus.PASS).scalar() or 0
    pending = db.query(func.count(Scan.id)).filter(Scan.status.in_([ScanStatus.REVIEW_REQUIRED, ScanStatus.NOT_A_PRODUCT, ScanStatus.IMAGE_QUALITY_INSUFFICIENT])).scalar() or 0
    high_sev = db.query(func.count(Violation.id)).filter(
        Violation.severity.in_([ViolationSeverity.HIGH, ViolationSeverity.CRITICAL]),
        Violation.status == ViolationStatus.FAIL
    ).scalar() or 0
    recent = db.query(Scan).order_by(Scan.created_at.desc()).limit(5).all()
    by_cat = db.query(Scan.category, func.count(Scan.id)).group_by(Scan.category).all()
    return {
        "total_scans": total,
        "compliant": compliant,
        "violations": violations,
        "pending_review": pending,
        "high_severity": high_sev,
        "compliance_rate": round((compliant / total * 100), 1) if total > 0 else 0,
        "recent_scans": [
            {"id": s.id, "product_name": s.product_name, "category": s.category,
             "status": s.overall_status.value if s.overall_status and hasattr(s.overall_status, "value") else s.overall_status,
             "score": s.compliance_score, "created_at": s.created_at}
            for s in recent
        ],
        "by_category": [{"category": c, "count": n} for c, n in by_cat],
    }