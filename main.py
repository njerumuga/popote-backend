import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import listings, enquiries, auth, contact
from database import Base, engine, SessionLocal
import models, auth_utils

# Sync Database Tables
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database sync error: {e}")

app = FastAPI(title="Popote Boutique API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jazzy-fudge-55f084.netlify.app",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🚀 Force Seed Admin (at /api/force-seed-admin)
@app.get("/api/force-seed-admin")
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
        return {"status": "Admin created"}
    return {"status": "Admin exists"}

# Register Routers
app.include_router(auth.router, prefix="/api")
app.include_router(listings.router, prefix="/api")
app.include_router(enquiries.router, prefix="/api")
app.include_router(contact.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Boutique API is live", "hint": "Use /api prefix"}