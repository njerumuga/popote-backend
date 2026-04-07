from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
import models, schemas

router = APIRouter(prefix="/contact", tags=["Contact"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def send_contact_message(contact: schemas.ContactMessageCreate, db: Session = Depends(get_db)):
    db_msg = models.ContactMessage(**contact.model_dump())
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    return {"status": "success", "message": "Your message has been received!"}