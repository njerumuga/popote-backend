import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import listings, users, enquiries, auth, contact
from database import Base, engine, SessionLocal
import models, auth_utils

# ═══ DATABASE SYNC ═══
# This ensures your Render PostgreSQL tables are created automatically
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database sync error: {e}")

app = FastAPI(title="Popote Boutique API")

# ═══ ELITE CORS SETTINGS ═══
# Updated guest list to allow your new Netlify frontend to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jazzy-fudge-55f084.netlify.app", # 🆕 Updated Netlify URL (No trailing slash)
        "http://localhost:3000"                  # Local Development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🚀 TEMPORARY: Force Seed Admin on Render
# Visit https://popote-backend.onrender.com/force-seed-admin once to ensure admin exists
@app.get("/force-seed-admin")
def seed():
    db = SessionLocal()
    email = "admin@popote.com"
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        new_user = models.User(
            email=email,
            password=auth_utils.get_password_hash("admin123")
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"status": "Admin created successfully"}
    return {"status": "Admin already exists"}

# Registering Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(listings.router)
app.include_router(enquiries.router)
app.include_router(contact.router)

@app.get("/")
def root():
    return {
        "message": "Popote Boutique API is live",
        "status": "Operational",
        "environment": "Render Cloud"
    }