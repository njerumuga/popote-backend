from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
import models, schemas

router = APIRouter(prefix="/enquiries", tags=["Enquiries"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def create_enquiry(enquiry: schemas.EnquiryCreate, db: Session = Depends(get_db)):
    db_enquiry = models.Enquiry(**enquiry.dict())
    db.add(db_enquiry)
    db.commit()
    db.refresh(db_enquiry)
    return db_enquiry
