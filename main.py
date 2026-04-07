import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import listings, users, enquiries, auth, contact
from database import Base, engine

# Create the uploads folder if it doesn't exist
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Automatically create tables in PostgreSQL
# Note: This requires a valid DATABASE_URL to be set in Render Environment
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database sync error: {e}")

app = FastAPI(title="Popote Listings API")

# ✅ REFINED CORS: Added your specific Vercel URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://popote-frontend-react.vercel.app",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files (Keep for local, but Supabase handles cloud)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Register routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(listings.router)
app.include_router(enquiries.router)
app.include_router(contact.router)

@app.get("/")
def root():
    return {"message": "Popote Listings API is live on Render"}