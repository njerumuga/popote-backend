import os
import uuid
import cloudinary
import cloudinary.uploader
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models

cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET"),
    secure = True
)

router = APIRouter(prefix="/listings", tags=["Listings"])

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.get("/")
def get_listings(category: Optional[str] = Query(None), region: Optional[str] = Query(None), db: Session = Depends(get_db)):
    query = db.query(models.Listing).filter(models.Listing.status == "approved")
    if category: query = query.filter(models.Listing.category == category)
    if region: query = query.filter(models.Listing.region == region)
    return query.all()

@router.post("/")
async def create_listing(
    title: str = Form(...),
    region: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    description: Optional[str] = Form(None),
    youtube_url: Optional[str] = Form(None),
    beds: Optional[str] = Form(None),
    baths: Optional[str] = Form(None),
    sqm: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    files: List[UploadFile] = File(...), # 📸 Receives multiple images
    db: Session = Depends(get_db)
):
    uploaded_urls = []
    # 🛠️ LOOP FIX: Upload every image selected
    for file in files:
        try:
            result = cloudinary.uploader.upload(file.file, folder="popote_boutique")
            uploaded_urls.append(result.get("secure_url"))
        except Exception as e:
            print(f"Upload error: {e}")

    db_listing = models.Listing(
        title=title,
        region=region,
        category=category,
        price=price,
        description=description,
        youtube_url=youtube_url,
        beds=beds,
        baths=baths,
        sqm=sqm,
        location=location,
        image_url=",".join(uploaded_urls), # 🔗 Links joined by commas
        status="approved"
    )
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing

@router.delete("/{listing_id}")
def delete_listing(listing_id: int, db: Session = Depends(get_db)):
    db_listing = db.query(models.Listing).filter(models.Listing.id == listing_id).first()
    if not db_listing: raise HTTPException(status_code=404)
    db.delete(db_listing)
    db.commit()
    return {"message": "Listing removed"}