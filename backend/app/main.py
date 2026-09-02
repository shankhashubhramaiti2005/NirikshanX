import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .config import settings
from .database import Base, engine
from .routers import auth, scans, dashboard, reports

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-Powered Packaged Commodity Compliance System",
    version="1.0.0",
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(scans.router, prefix="/scans", tags=["Scans"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(reports.router, prefix="/reports", tags=["Reports"])

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))

if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.on_event("startup")
def on_startup():
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    from sqlalchemy import text
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE scans ADD COLUMN ai_debug_metrics JSON"))
            conn.commit()
        except Exception:
            pass

    from .database import SessionLocal
    from .models.user import User, UserRole
    from .auth.security import hash_password
    db = SessionLocal()
    try:
        if not db.query(User).first():
            admin = User(
                email="admin@nirikshanx.gov.in",
                full_name="Admin User",
                hashed_password=hash_password("password123"),
                role=UserRole.ADMIN,
                is_superuser=True,
                is_active=True,
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()

@app.get("/app", response_class=FileResponse, tags=["Frontend"])
@app.get("/", response_class=FileResponse, tags=["Frontend"])
def serve_app():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"status": "ok", "project": settings.PROJECT_NAME, "version": "1.0.0", "demo_mode": settings.DEMO_MODE}