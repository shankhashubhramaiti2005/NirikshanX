# NirikshanX 🔍🇮🇳

**AI-Powered Packaged Commodity Compliance & Verification System**

NirikshanX is an advanced AI  system designed for verifying packaged commodity labels according to Legal Metrology guidelines and regulatory compliance standards.

## 🚀 Features

- **Automated Label Inspection**: Image quality check, blur detection, object detection, and ROI extraction.
- **OCR Engine**: Multi-engine OCR (Tesseract / EasyOCR / EasyOCR-fallback) with preprocessing and text post-correction.
- **Compliance Rules Engine**: Legal Metrology verification (MRP, Net Weight, Mfd Date, Expiry, Manufacturer Details, Country of Origin, Customer Care).
- **Interactive Web Interface**: Single Page Application (SPA) dashboard for upload, live analysis, batch scan, report generation, and analytics.
- **RESTful API**: FastAPI backend with JWT authentication, RBAC, scan management, and PDF report generation.

## 🛠️ Architecture

- **Backend**: FastAPI, SQLAlchemy, SQLite, Pydantic, OpenCV, Pillow, EasyOCR/PyTesseract, ReportLab.
- **Frontend**: HTML5, CSS3 (Modern Glassmorphism Design System), Vanilla JS, Chart.js.

## 🏁 Quickstart

### Backend Setup
```bash
cd backend
python -m venv venv
# Activate virtual environment
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Accessing the Web UI
Open your browser and navigate to `http://localhost:8000/` or `http://localhost:8000/app`.

## 📜 License
MIT License
