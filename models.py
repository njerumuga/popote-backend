from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

class Listing(Base):
    __tablename__ = "listings"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float)
    region = Column(String)
    location = Column(String, nullable=True)
    category = Column(String)
    beds = Column(String, nullable=True)
    baths = Column(String, nullable=True)
    sqm = Column(String, nullable=True)
    image_url = Column(Text) # Holds multiple URLs separated by commas
    youtube_url = Column(String, nullable=True)
    status = Column(String, default="approved")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

class Enquiry(Base):
    __tablename__ = "enquiries"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String)
    email = Column(String, nullable=True)
    property = Column(String)
    message = Column(Text, nullable=True)
    status = Column(String, default="New")
    date = Column(DateTime, default=datetime.datetime.utcnow)

class ContactMessage(Base):
    __tablename__ = "contact_messages"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    message = Column(Text)