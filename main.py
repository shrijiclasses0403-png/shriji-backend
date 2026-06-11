from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

from app.database import engine, Base, SessionLocal
from app import models
from app.utils.security import hash_password
from app.routers.auth import router as auth_router
from app.routers.students import router as students_router
from app.routers.fees import router as fees_router
from app.routers.academics import marks_router, attendance_router, notes_router

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title       = "Shri Ji Classes API",
    description = "Backend API for Shri Ji Classes management system",
    version     = "1.0.0",
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)

# CORS — allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins   = [os.getenv("FRONTEND_URL", "http://localhost:3000"), "http://localhost:3000"],
    allow_credentials = True,
    allow_methods   = ["*"],
    allow_headers   = ["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(students_router)
app.include_router(fees_router)
app.include_router(marks_router)
app.include_router(attendance_router)
app.include_router(notes_router)


@app.get("/")
def root():
    return {
        "message": "Shri Ji Classes API is running 🎓",
        "docs":    "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


# ── Seed default admin on first run ───────────────────────────────────────────
def seed_admin():
    db = SessionLocal()
    try:
        existing = db.query(models.Admin).filter(models.Admin.username == os.getenv("ADMIN_USERNAME", "admin")).first()
        if not existing:
            admin = models.Admin(
                username        = os.getenv("ADMIN_USERNAME", "admin"),
                hashed_password = hash_password(os.getenv("ADMIN_PASSWORD", "admin@shriji123")),
                name            = "Admin",
            )
            db.add(admin)
            db.commit()
            print("✅ Default admin created")
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    seed_admin()
    print("🚀 Shri Ji Classes API started")
    print("📖 API docs: http://localhost:8000/docs")
