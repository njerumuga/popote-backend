import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import listings, users, enquiries, auth, contact # ✅ Added contact
from database import Base, engine

# Create the uploads folder if it doesn't exist
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Automatically create tables in PostgreSQL
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Popote Listings API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Register routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(listings.router)
app.include_router(enquiries.router)
app.include_router(contact.router) # ✅ Added contact router

@app.get("/")
def root():
    return {"message": "Popote Listings API is live with Contact Support"}