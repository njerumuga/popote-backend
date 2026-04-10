from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    listings = relationship("Listing", back_populates="owner")


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    region = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    category = Column(String(255), nullable=False, index=True)
    beds = Column(String(50), nullable=True)
    baths = Column(String(50), nullable=True)
    sqm = Column(String(50), nullable=True)
    image_url = Column(Text, nullable=True)  # Comma-separated URLs
    youtube_url = Column(String(500), nullable=True)
    status = Column(String(50), default="approved", index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    owner = relationship("User", back_populates="listings")


class Enquiry(Base):
    __tablename__ = "enquiries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=True)
    property = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    status = Column(String(50), default="New", index=True)
    date = Column(DateTime, default=datetime.datetime.utcnow, index=True)


class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)