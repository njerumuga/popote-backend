import uuid
import os
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from supabase import create_client, Client
from dotenv import load_dotenv

from database import SessionLocal
import models, schemas

load_dotenv()

# ═══ SUPABASE CLOUD STORAGE CONFIG ═══
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
BUCKET_NAME = "property-images"

router = APIRouter(prefix="/listings", tags=["Listings"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 1. GET ALL LISTINGS
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

    # If user is not logged in, they only see 'approved' listings
    if not include_pending:
        query = query.filter(models.Listing.status == "approved")

    if category:
        query = query.filter(models.Listing.category == category)
    if region:
        query = query.filter(models.Listing.region == region)
    if max_price:
        query = query.filter(models.Listing.price <= max_price)
    if search:
        query = query.filter(models.Listing.title.ilike(f"%{search}%"))

    return query.all()


# 2. CREATE NEW LISTING
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
            # Generate unique filename for cloud storage
            file_ext = file.filename.split(".")[-1]
            unique_filename = f"{uuid.uuid4()}.{file_ext}"

            # Upload to Supabase Storage
            file_content = await file.read()
            supabase.storage.from_(BUCKET_NAME).upload(
                path=unique_filename,
                file=file_content,
                file_options={"content-type": file.content_type}
            )

            # Retrieve the public URL for the database
            res = supabase.storage.from_(BUCKET_NAME).get_public_url(unique_filename)
            final_image_url = res
        except Exception as e:
            print(f"Cloud Upload Error: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload image to cloud")

    db_listing = models.Listing(
        title=title,
        region=region,
        category=category,
        price=price,
        image_url=final_image_url,
        status="approved"  # ✅ Changed to 'approved' so uploads are live instantly
    )

    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing


# 3. APPROVE LISTING (FIXES THE 404 ERROR)
@router.patch("/{listing_id}/approve")
def approve_listing(listing_id: int, db: Session = Depends(get_db)):
    db_listing = db.query(models.Listing).filter(models.Listing.id == listing_id).first()

    if not db_listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    db_listing.status = "approved"
    db.commit()
    db.refresh(db_listing)

    return {"message": "Listing approved successfully"}


# 4. DELETE LISTING
@router.delete("/{listing_id}")
def delete_listing(listing_id: int, db: Session = Depends(get_db)):
    db_listing = db.query(models.Listing).filter(models.Listing.id == listing_id).first()

    if not db_listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    # Delete the image from Supabase Storage before removing DB record
    if db_listing.image_url:
        try:
            file_name = db_listing.image_url.split("/")[-1]
            supabase.storage.from_(BUCKET_NAME).remove([file_name])
        except Exception as e:
            print(f"Error deleting cloud file: {e}")

    db.delete(db_listing)
    db.commit()
    return {"message": "Listing and cloud image deleted successfully"}