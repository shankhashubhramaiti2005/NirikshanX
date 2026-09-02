import os
import shutil
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..config import settings
from ..models.scan import Scan
from ..models.declaration import Declaration
from ..models.violation import Violation
from ..pipeline import ImageValidationPipeline

router = APIRouter()
pipeline = ImageValidationPipeline()

@router.post("/upload")
def upload_and_scan(
    file: UploadFile = File(...),
    category: Optional[str] = Form("general"),
    db: Session = Depends(get_db)
):
    # Validate image extension
    allowed_exts = {".jpg", ".jpeg", ".png", ".webp"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"Unsupported file format '{ext}'. Allowed: {allowed_exts}")

    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Process through pipeline
    result = pipeline.process_image(file_path, category=category)

    # Save to database
    scan = Scan(
        image_filename=file.filename,
        image_path=file_path,
        is_valid=result.get("is_valid", False),
        status=result.get("status", "UNKNOWN"),
        processing_time_seconds=result.get("processing_time_seconds", 0.0),
        quality_metrics=result.get("quality_metrics"),
        product_metrics=result.get("product_metrics"),
        ocr_metrics=result.get("ocr_metrics"),
        compliance_result=result.get("compliance_result"),
        ai_debug_metrics={
            "stage_failed": result.get("stage_failed"),
            "reasons": result.get("reasons")
        }
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    # Save extracted declarations
    ocr_declarations = result.get("ocr_metrics", {}).get("declarations", {})
    declaration = Declaration(
        scan_id=scan.id,
        mrp=ocr_declarations.get("mrp"),
        net_quantity=ocr_declarations.get("net_quantity"),
        mfd_date=ocr_declarations.get("mfd_date"),
        expiry_date=ocr_declarations.get("expiry_date"),
        country_of_origin=ocr_declarations.get("country_of_origin"),
        customer_care=ocr_declarations.get("customer_care"),
        manufacturer_details=ocr_declarations.get("manufacturer_details")
    )
    db.add(declaration)

    # Save violations
    violations_list = result.get("compliance_result", {}).get("violations", [])
    for v in violations_list:
        violation = Violation(
            scan_id=scan.id,
            rule_id=v.get("rule_id", "LM_GENERIC"),
            field_name=v.get("field_name", "UNKNOWN"),
            severity=v.get("severity", "HIGH"),
            description=v.get("description", "")
        )
        db.add(violation)

    db.commit()

    return {
        "scan_id": scan.id,
        "filename": scan.image_filename,
        "result": result
    }

@router.get("/{scan_id}")
def get_scan_by_id(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan

@router.get("/")
def list_scans(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    scans = db.query(Scan).order_by(Scan.created_at.desc()).offset(skip).limit(limit).all()
    return scans
