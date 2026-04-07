import uuid
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models, schemas
from typing import List, Optional
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

# ═══ SUPABASE CLOUD STORAGE CONFIG ═══
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
BUCKET_NAME = "property-images"  # Ensure you created this in Supabase Storage!

router = APIRouter(prefix="/listings", tags=["Listings"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
            # 1. Generate unique cloud filename
            file_ext = file.filename.split(".")[-1]
            unique_filename = f"{uuid.uuid4()}.{file_ext}"

            # 2. Upload to Supabase Storage
            file_content = await file.read()
            supabase.storage.from_(BUCKET_NAME).upload(
                path=unique_filename,
                file=file_content,
                file_options={"content-type": file.content_type}
            )

            # 3. Get the Public URL
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
        image_url=final_image_url,  # Now stores 'https://...' instead of 'image.jpg'
        status="pending"
    )

    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing


@router.delete("/{listing_id}")
def delete_listing(listing_id: int, db: Session = Depends(get_db)):
    db_listing = db.query(models.Listing).filter(models.Listing.id == listing_id).first()
    if not db_listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    # 1. Delete from Supabase Storage if it exists
    if db_listing.image_url:
        try:
            # Extract filename from URL
            file_name = db_listing.image_url.split("/")[-1]
            supabase.storage.from_(BUCKET_NAME).remove([file_name])
        except Exception as e:
            print(f"Error deleting cloud file: {e}")

    # 2. Delete from Database
    db.delete(db_listing)
    db.commit()
    return {"message": "Listing and cloud image deleted successfully"}