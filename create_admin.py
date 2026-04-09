import os
import bcrypt
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import models

# ═══ 1. USE THE EXTERNAL URL FROM YOUR RENDER SCREENSHOT ═══
# Note: External is for your laptop, Internal is for Render's backend
RAW_URL = "postgresql://popote_db_user:K2nqesEpjHdreV68AjuHKAImjaSycaB2@dpg-d7bvc61j2pic739u0lu0-a.oregon-postgres.render.com:5432/popote_db"

# URL Fixer
DATABASE_URL = RAW_URL.replace("postgres://", "postgresql://", 1) if RAW_URL.startswith("postgres://") else RAW_URL

# Setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()


def create_initial_admin():
    email = "admin@popote.com"
    password = os.getenv("ADMIN_SETUP_PASSWORD")

    if not password:
        print("❌ ERROR: Set the password using $env:ADMIN_SETUP_PASSWORD='yourpass'")
        return

    try:
        # Check connection
        db.execute(text("SELECT 1"))

        exists = db.query(models.User).filter(models.User.email == email).first()
        if exists:
            print("Admin already exists!")
            return

        # ═══ NATIVE BCRYPT HASHING ═══
        hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed_str = hashed_bytes.decode('utf-8')

        # ═══ CREATE USER (Matching your models.py) ═══
        new_user = models.User(
            email=email,
            password=hashed_str
        )

        db.add(new_user)
        db.commit()
        print(f"✅ SUCCESS: Admin '{email}' created in Render DB.")

    except Exception as e:
        db.rollback()
        print(f"❌ DATABASE ERROR: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_initial_admin()