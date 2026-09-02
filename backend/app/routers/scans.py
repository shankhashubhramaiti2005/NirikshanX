import os, uuid, shutil
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..models.user import User
from ..models import Scan, Declaration, Violation, Case, ScanStatus, ViolationStatus, ViolationSeverity
from ..dependencies.auth import get_current_user
from ..ai.pipeline import run_validation_pipeline
from ..config import settings

router = APIRouter()
CATEGORIES = ["GENERAL", "FOOD", "COSMETICS", "ELECTRONICS", "MEDICINE"]

class ScanOut(BaseModel):
    id: int
    product_name: str
    category: str
    status: str
    compliance_score: Optional[float] = None
    overall_status: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}

def _process(scan_id: int, image_path: str, category: str, scenario: int):
    from ..database import SessionLocal
    db = SessionLocal()
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            return
        scan.status = ScanStatus.PROCESSING
        db.commit()
        pipeline_res = run_validation_pipeline(image_path, category, scenario, product_name_hint=scan.product_name)

        for field, info in pipeline_res.get("declarations", {}).items():
            db.add(Declaration(
                scan_id=scan_id,
                field_name=field,
                extracted_value=info.get("value"),
                confidence=float(info.get("confidence", 0.0)),
                is_present=bool(info.get("value")),
            ))

        sev_map = {"LOW": ViolationSeverity.LOW, "MEDIUM": ViolationSeverity.MEDIUM,
                   "HIGH": ViolationSeverity.HIGH, "CRITICAL": ViolationSeverity.CRITICAL}
        st_map = {"FAIL": ViolationStatus.FAIL, "WARNING": ViolationStatus.WARNING,
                  "REVIEW_REQUIRED": ViolationStatus.REVIEW_REQUIRED,
                  "NOT_A_PRODUCT": ViolationStatus.NOT_A_PRODUCT,
                  "IMAGE_QUALITY_INSUFFICIENT": ViolationStatus.IMAGE_QUALITY_INSUFFICIENT}

        for check in pipeline_res.get("checks", []):
            if check["status"] != "PASS":
                db.add(Violation(
                    scan_id=scan_id,
                    rule_id=check["rule_id"],
                    field=check["field"],
                    status=st_map.get(check["status"], ViolationStatus.FAIL),
                    severity=sev_map.get(check["severity"], ViolationSeverity.MEDIUM),
                    message=check["message"],
                    evidence=check.get("evidence"),
                    confidence=check.get("confidence", 1.0),
                ))

        overall_str = pipeline_res["overall_status"]
        overall_map = {
            "PASS": ViolationStatus.PASS,
            "FAIL": ViolationStatus.FAIL,
            "WARNING": ViolationStatus.WARNING,
            "REVIEW_REQUIRED": ViolationStatus.REVIEW_REQUIRED,
            "NOT_A_PRODUCT": ViolationStatus.NOT_A_PRODUCT,
            "IMAGE_QUALITY_INSUFFICIENT": ViolationStatus.IMAGE_QUALITY_INSUFFICIENT
        }
        scan_st_map = {
            "COMPLETED": ScanStatus.COMPLETED,
            "REVIEW_REQUIRED": ScanStatus.REVIEW_REQUIRED,
            "NOT_A_PRODUCT": ScanStatus.NOT_A_PRODUCT,
            "IMAGE_QUALITY_INSUFFICIENT": ScanStatus.IMAGE_QUALITY_INSUFFICIENT
        }

        scan.compliance_score = pipeline_res["compliance_score"]
        scan.overall_status = overall_map.get(overall_str, ViolationStatus.REVIEW_REQUIRED)
        scan.status = scan_st_map.get(pipeline_res.get("scan_status"), ScanStatus.COMPLETED)
        scan.ai_debug_metrics = pipeline_res.get("ai_debug_metrics")
        scan.completed_at = datetime.utcnow()

        case_num = f"NX-{datetime.utcnow().strftime('%Y%m%d')}-{scan_id:04d}"
        db.add(Case(scan_id=scan_id, case_number=case_num))
        db.commit()
    except Exception as e:
        scan.status = ScanStatus.FAILED
        db.commit()
        raise
    finally:
        db.close()

@router.post("/submit", response_model=ScanOut)
async def submit_scan(
    background_tasks: BackgroundTasks,
    product_name: str = Form(...),
    category: str = Form("FOOD"),
    scenario: int = Form(0),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if category not in CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Category must be one of {CATEGORIES}")
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    image_path = ""
    if image and image.filename:
        ext = os.path.splitext(image.filename)[1] or ".jpg"
        fname = f"{uuid.uuid4().hex}{ext}"
        image_path = os.path.join(settings.UPLOAD_DIR, fname)
        with open(image_path, "wb") as f:
            shutil.copyfileobj(image.file, f)

    scan = Scan(user_id=current_user.id, product_name=product_name,
                category=category, image_path=image_path, status=ScanStatus.PENDING)
    db.add(scan)
    db.commit()
    db.refresh(scan)
    background_tasks.add_task(_process, scan.id, image_path, category, scenario)
    return scan

@router.get("/{scan_id}")
def get_scan(scan_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return {
        "id": scan.id, "product_name": scan.product_name, "category": scan.category,
        "status": scan.status.value if hasattr(scan.status, "value") else scan.status,
        "compliance_score": scan.compliance_score,
        "overall_status": scan.overall_status.value if scan.overall_status and hasattr(scan.overall_status, "value") else scan.overall_status,
        "created_at": scan.created_at, "completed_at": scan.completed_at,
        "ai_debug_metrics": scan.ai_debug_metrics,
        "declarations": [{"field": d.field_name, "value": d.extracted_value, "confidence": d.confidence, "is_present": d.is_present} for d in scan.declarations],
        "violations": [{"rule_id": v.rule_id, "field": v.field,
                         "status": v.status.value if hasattr(v.status, "value") else v.status,
                         "severity": v.severity.value if hasattr(v.severity, "value") else v.severity,
                         "message": v.message, "evidence": v.evidence, "confidence": v.confidence} for v in scan.violations],
    }

@router.get("/")
def list_scans(skip: int = 0, limit: int = 20, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(Scan)
    if not current_user.is_superuser and current_user.role.value not in ("ADMIN","ENFORCEMENT_OFFICER","INSPECTOR"):
        q = q.filter(Scan.user_id == current_user.id)
    scans = q.order_by(Scan.created_at.desc()).offset(skip).limit(limit).all()
    return [ScanOut.model_validate(s) for s in scans]