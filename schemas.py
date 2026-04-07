from pydantic import BaseModel, ConfigDict
from typing import Optional

# User Schemas
class UserCreate(BaseModel):
    email: str
    password: str

# Listing Schemas
class ListingCreate(BaseModel):
    title: str
    region: str
    category: str
    price: float
    image_url: Optional[str] = None

class Listing(ListingCreate):
    id: int
    status: str
    model_config = ConfigDict(from_attributes=True)

# Enquiry Schemas
class EnquiryCreate(BaseModel):
    message: str
    listing_id: int

# ✅ Contact Schemas (Corrected Indentation)
class ContactMessageCreate(BaseModel):
    name: str
    email: str
    message: str

class ContactMessage(ContactMessageCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)