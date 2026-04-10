import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from routers import listings, enquiries, auth, contact
from database import Base, engine, SessionLocal
import models
import auth_utils


# Initialize database
def init_db():
    """Create all tables defined in models."""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/verified")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")


# Run on startup
init_db()

app = FastAPI(title="Popote Boutique API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://jazzy-fudge-55f084.netlify.app", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# 🔧 DATABASE MIGRATION & REPAIR ENDPOINTS
# ============================================================================

@app.get("/api/database/schema")
def check_schema(db: Session = Depends(get_db)):
    """Check current database schema and compare with models."""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        schema_info = {}
        for table_name in tables:
            columns = inspector.get_columns(table_name)
            schema_info[table_name] = [col['name'] for col in columns]

        return {
            "status": "success",
            "tables": tables,
            "schema": schema_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/database/migrate")
def migrate_database(db: Session = Depends(get_db)):
    """
    Safely migrate database schema to match SQLAlchemy models.
    This adds missing columns without dropping existing data.
    """
    try:
        # Get current schema
        inspector = inspect(engine)
        existing_columns = {col['name'] for col in inspector.get_columns('listings')}

        # Define all required columns
        required_columns = {
            'id': 'INTEGER PRIMARY KEY',
            'title': 'VARCHAR(255)',
            'description': 'TEXT',
            'price': 'FLOAT',
            'region': 'VARCHAR(255)',
            'location': 'VARCHAR(255)',
            'category': 'VARCHAR(255)',
            'beds': 'VARCHAR(50)',
            'baths': 'VARCHAR(50)',
            'sqm': 'VARCHAR(50)',
            'image_url': 'TEXT',
            'youtube_url': 'VARCHAR(500)',
            'status': "VARCHAR(50) DEFAULT 'approved'",
            'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'owner_id': 'INTEGER'
        }

        migrations = []
        missing_columns = set(required_columns.keys()) - existing_columns

        if missing_columns:
            for col in missing_columns:
                col_type = required_columns[col]
                migrations.append(f"ALTER TABLE listings ADD COLUMN {col} {col_type};")

        if migrations:
            for migration in migrations:
                print(f"Executing: {migration}")
                db.execute(text(migration))
            db.commit()

            return {
                "status": "success",
                "message": f"Added {len(migrations)} missing columns",
                "columns_added": list(missing_columns)
            }
        else:
            return {
                "status": "success",
                "message": "Database schema is already up to date",
                "columns_added": []
            }

    except Exception as e:
        db.rollback()
        print(f"Migration error: {e}")
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")


@app.post("/api/database/reset-tables")
def reset_tables(db: Session = Depends(get_db)):
    """
    ⚠️  DANGEROUS: Drop and recreate all tables.
    Only use if you want to clear all data and start fresh.
    """
    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        return {
            "status": "success",
            "message": "All tables dropped and recreated",
            "warning": "All data has been deleted"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 🔐 USER SEEDING
# ============================================================================

@app.post("/api/admin/seed-admin")
def seed_admin(db: Session = Depends(get_db)):
    """Create default admin user if it doesn't exist."""
    try:
        email = "admin@popote.com"
        user = db.query(models.User).filter(models.User.email == email).first()

        if not user:
            new_user = models.User(
                email=email,
                password=auth_utils.get_password_hash("admin123")
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            return {
                "status": "created",
                "message": "Admin user created",
                "email": email,
                "password": "admin123"
            }

        return {
            "status": "exists",
            "message": "Admin user already exists",
            "email": email
        }

    except Exception as e:
        db.rollback()
        print(f"Error seeding admin: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 📡 ROUTERS
# ============================================================================

app.include_router(auth.router, prefix="/api")
app.include_router(listings.router, prefix="/api")
app.include_router(enquiries.router, prefix="/api")
app.include_router(contact.router, prefix="/api")


# ============================================================================
# 🏠 ROOT ENDPOINT
# ============================================================================

@app.get("/")
def root():
    return {
        "message": "Boutique API is live",
        "version": "1.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "database_schema": "/api/database/schema",
            "database_migrate": "/api/database/migrate"
        }
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Check API and database health."""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }