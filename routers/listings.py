import os
import uuid
import cloudinary
import cloudinary.uploader
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models, schemas

# ═══ CLOUDINARY CONFIGURATION ═══
# These credentials must be set in your Render Environment Variables
cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET"),
    secure = True
)

router = APIRouter(prefix="/listings", tags=["Listings"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. FETCH ALL LISTINGS
@router.get("/", response_model=List[schemas.Listing])
def get_listings(
        category: Optional[str] = Query(None),
        region: Optional[str] = Query(None),
        search: Optional[str] = Query(None),
        max_price: Optional[float] = Query(None),
        include_pending: bool = Query(False),
        db: Session = Depends(get_db)
):
    query = db.query(models.Listing)

    # Standard public view only shows 'approved'
    if not include_pending:
        query = query.filter(models.Listing.status == "approved")

    # Elite Search Filters
    if category:
        query = query.filter(models.Listing.category == category)
    if region:
        query = query.filter(models.Listing.region == region)
    if max_price:
        query = query.filter(models.Listing.price <= max_price)
    if search:
        query = query.filter(models.Listing.title.ilike(f"%{search}%"))

    return query.all()

# 2. ARCHIVE NEW ESTATE (CLOUDINARY UPLOAD)
@router.post("/")
async def create_listing(
        title: str = Form(...),
        region: str = Form(...),
        category: str = Form(...),
        price: float = Form(...),
        file: Optional[UploadFile] = File(None),
        db: Session = Depends(get_db)
):
    final_image_url = ""

    if file:
        try:
            # Upload to Cloudinary with Luxury Auto-Optimization
            upload_result = cloudinary.uploader.upload(
                file.file,
                folder="popote_boutique",
                public_id=f"{uuid.uuid4()}",
                transformation=[
                    {'quality': "auto", 'fetch_format': "auto"}
                ]
            )
            final_image_url = upload_result.get("secure_url")
        except Exception as e:
            print(f"Cloudinary Error: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload image to Cloudinary")

    db_listing = models.Listing(
        title=title,
        region=region,
        category=category,
        price=price,
        image_url=final_image_url,
        status="approved"  # New uploads go live immediately
    )

    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing

# 3. APPROVE LISTING
@router.patch("/{listing_id}/approve")
def approve_listing(listing_id: int, db: Session = Depends(get_db)):
    db_listing = db.query(models.Listing).filter(models.Listing.id == listing_id).first()

    if not db_listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    db_listing.status = "approved"
    db.commit()
    db.refresh(db_listing)

    return {"message": "Listing approved successfully"}

# 4. REMOVE ESTATE
@router.delete("/{listing_id}")
def delete_listing(listing_id: int, db: Session = Depends(get_db)):
    db_listing = db.query(models.Listing).filter(models.Listing.id == listing_id).first()

    if not db_listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    # Note: For a clean removal, we'd delete from Cloudinary too,
    # but deleting from the DB is enough for the site to update.
    db.delete(db_listing)
    db.commit()
    return {"message": "Listing removed from archive"}