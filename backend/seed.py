import os
from app.database import SessionLocal, Base, engine
from app.models.user import User, UserRole
from app.models.scan import Scan
from app.models.declaration import Declaration
from app.models.violation import Violation
from app.auth.security import hash_password

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.email == "admin@nirikshanx.gov.in").first():
            admin = User(
                email="admin@nirikshanx.gov.in",
                full_name="Chief Metrology Officer",
                hashed_password=hash_password("admin123"),
                role=UserRole.ADMIN,
                is_superuser=True,
                is_active=True
            )
            db.add(admin)
            
            inspector = User(
                email="inspector@nirikshanx.gov.in",
                full_name="Field Inspector Kolkata",
                hashed_password=hash_password("inspector123"),
                role=UserRole.INSPECTOR,
                is_active=True
            )
            db.add(inspector)
            db.commit()
            print("Database seeded with default users.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
