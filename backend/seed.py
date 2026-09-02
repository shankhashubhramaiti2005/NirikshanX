import sys
sys.path.insert(0, '.')
from app.database import Base, engine, SessionLocal
from app.models.user import User, UserRole
from app.security import get_password_hash

Base.metadata.create_all(bind=engine)
db = SessionLocal()
existing = db.query(User).filter(User.email == 'admin@nirikshanx.gov.in').first()
if not existing:
    admin = User(
        email='admin@nirikshanx.gov.in',
        full_name='Admin User',
        hashed_password=get_password_hash('password123'),
        role=UserRole.ADMIN,
        is_superuser=True,
        is_active=True,
    )
    db.add(admin)
    db.commit()
    print('Admin user seeded: admin@nirikshanx.gov.in / password123')
else:
    print('Admin already exists.')
db.close()
