import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
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
    allow_origins=["https://jazzy-fudge-55f084.netlify.app", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# 🛠️ THE CRITICAL FIX: Visit https://popote-backend.onrender.com/api/fix-database-columns
@app.get("/api/fix-database-columns")
def migrate_db(db: Session = Depends(get_db)):
    try:
        # Adds all columns that your error log said were missing
        sql = """
        ALTER TABLE listings 
        ADD COLUMN IF NOT EXISTS description TEXT,
        ADD COLUMN IF NOT EXISTS location VARCHAR,
        ADD COLUMN IF NOT EXISTS beds VARCHAR,
        ADD COLUMN IF NOT EXISTS baths VARCHAR,
        ADD COLUMN IF NOT EXISTS sqm VARCHAR,
        ADD COLUMN IF NOT EXISTS youtube_url VARCHAR,
        ADD COLUMN IF NOT EXISTS status VARCHAR DEFAULT 'approved',
        ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW(),
        ADD COLUMN IF NOT EXISTS owner_id INTEGER;
        """
        db.execute(text(sql))
        db.commit()
        return {"status": "Success", "message": "Database columns added successfully."}
    except Exception as e:
        return {"status": "Error", "detail": str(e)}

@app.get("/api/force-seed-admin")
def seed():
    db = SessionLocal()
    email = "admin@popote.com"
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        new_user = models.User(email=email, password=auth_utils.get_password_hash("admin123"))
        db.add(new_user)
        db.commit()
        return {"status": "Admin created (admin123)"}
    return {"status": "Admin exists"}

app.include_router(auth.router, prefix="/api")
app.include_router(listings.router, prefix="/api")
app.include_router(enquiries.router, prefix="/api")
app.include_router(contact.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Boutique API is live"}