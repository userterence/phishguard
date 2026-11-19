from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import Base, engine, SessionLocal
from .models import User
from .security import hash_password
from .routers import auth, scan, reports, admin, analytics, awareness

app = FastAPI(title="PhishGuard AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.allowed_origins == "*" else settings.allowed_origins.split(","),
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def seed():
    """Create a default admin on first run so you can log in."""
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.role == "admin").first():
            db.add(User(email="admin@phishguard.local", full_name="System Administrator",
                        password_hash=hash_password("Admin@12345"), role="admin"))
            db.commit()
    finally:
        db.close()

for r in (auth, scan, reports, admin, analytics, awareness):
    app.include_router(r.router)

@app.get("/api/health")
def health():
    return {"ok": True, "service": "phishguard"}
