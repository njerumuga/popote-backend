from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    password = Column(String)

class Listing(Base):
    __tablename__ = "listings"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    region = Column(String)
    category = Column(String)
    price = Column(Float)
    image_url = Column(String)
    status = Column(String, default="pending")
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

class Enquiry(Base):
    __tablename__ = "enquiries"
    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)
    listing_id = Column(Integer, ForeignKey("listings.id"))

# ✅ Contact Model (Corrected Indentation)
class ContactMessage(Base):
    __tablename__ = "contact_messages"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    message = Column(String)