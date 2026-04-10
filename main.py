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
            schema_info[table_name] = [
                {
                    "name": col['name'],
                    "type": str(col['type']),
                    "nullable": col['nullable']
                }
                for col in columns
            ]

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
    Adds missing columns to all tables without dropping existing data.
    """
    try:
        inspector = inspect(engine)
        migrations = []

        # ===== LISTINGS TABLE =====
        listing_columns = {col['name'] for col in inspector.get_columns('listings')}

        required_listing_columns = {
            'id': 'INTEGER',
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

        listing_missing = set(required_listing_columns.keys()) - listing_columns

        if listing_missing:
            for col in listing_missing:
                col_type = required_listing_columns[col]
                migrations.append(
                    f"ALTER TABLE listings ADD COLUMN IF NOT EXISTS {col} {col_type};"
                )

        # ===== USERS TABLE =====
        user_columns = {col['name'] for col in inspector.get_columns('users')}

        required_user_columns = {
            'id': 'INTEGER',
            'email': 'VARCHAR(255)',
            'password': 'VARCHAR(255)',
            'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        }

        user_missing = set(required_user_columns.keys()) - user_columns

        if user_missing:
            for col in user_missing:
                col_type = required_user_columns[col]
                migrations.append(
                    f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {col} {col_type};"
                )

        # ===== ENQUIRIES TABLE =====
        enquiry_columns = {col['name'] for col in inspector.get_columns('enquiries')}

        required_enquiry_columns = {
            'id': 'INTEGER',
            'name': 'VARCHAR(255)',
            'phone': 'VARCHAR(20)',
            'email': 'VARCHAR(255)',
            'property': 'VARCHAR(255)',
            'message': 'TEXT',
            'status': "VARCHAR(50) DEFAULT 'New'",
            'date': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        }

        enquiry_missing = set(required_enquiry_columns.keys()) - enquiry_columns

        if enquiry_missing:
            for col in enquiry_missing:
                col_type = required_enquiry_columns[col]
                migrations.append(
                    f"ALTER TABLE enquiries ADD COLUMN IF NOT EXISTS {col} {col_type};"
                )

        # ===== CONTACT_MESSAGES TABLE =====
        contact_columns = {col['name'] for col in inspector.get_columns('contact_messages')}

        required_contact_columns = {
            'id': 'INTEGER',
            'name': 'VARCHAR(255)',
            'email': 'VARCHAR(255)',
            'message': 'TEXT',
            'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        }

        contact_missing = set(required_contact_columns.keys()) - contact_columns

        if contact_missing:
            for col in contact_missing:
                col_type = required_contact_columns[col]
                migrations.append(
                    f"ALTER TABLE contact_messages ADD COLUMN IF NOT EXISTS {col} {col_type};"
                )

        # Execute all migrations
        if migrations:
            for migration in migrations:
                print(f"🔄 Executing: {migration}")
                db.execute(text(migration))
            db.commit()

            all_missing = listing_missing | user_missing | enquiry_missing | contact_missing

            return {
                "status": "success",
                "message": f"✅ Added {len(migrations)} missing columns",
                "migrations_executed": len(migrations),
                "columns_added": {
                    "listings": list(listing_missing) if listing_missing else [],
                    "users": list(user_missing) if user_missing else [],
                    "enquiries": list(enquiry_missing) if enquiry_missing else [],
                    "contact_messages": list(contact_missing) if contact_missing else []
                }
            }
        else:
            return {
                "status": "success",
                "message": "✅ Database schema is already up to date",
                "migrations_executed": 0,
                "columns_added": {
                    "listings": [],
                    "users": [],
                    "enquiries": [],
                    "contact_messages": []
                }
            }

    except Exception as e:
        db.rollback()
        print(f"❌ Migration error: {e}")
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")


@app.post("/api/database/reset-tables")
def reset_tables(db: Session = Depends(get_db)):
    """
    ⚠️  DANGEROUS: Drop and recreate all tables.
    Only use if you want to clear all data and start fresh.
    This will DELETE ALL DATA in your database!
    """
    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        return {
            "status": "success",
            "message": "✅ All tables dropped and recreated",
            "warning": "⚠️  All data has been deleted permanently"
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
                "message": "✅ Admin user created successfully",
                "email": email,
                "password": "admin123",
                "warning": "⚠️  Change this password in production!"
            }

        return {
            "status": "exists",
            "message": "✅ Admin user already exists",
            "email": email
        }

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding admin: {e}")
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
        "message": "🎉 Popote Boutique API is live!",
        "version": "1.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "openapi": "/openapi.json",
            "health": "/health",
            "database_schema": "/api/database/schema",
            "database_migrate": "/api/database/migrate",
            "admin_seed": "/api/admin/seed-admin"
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
            "database": "connected",
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }