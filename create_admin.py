import os
import bcrypt
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import models

# ═══ DATABASE CONFIG ═══
RAW_URL = "postgresql://popote_db_user:K2nqesEpjHdreV68AjuHKAImjaSycaB2@dpg-d7bvc61j2pic739u0lu0-a.oregon-postgres.render.com:5432/popote_db"
DATABASE_URL = RAW_URL.replace("postgres://", "postgresql://", 1) if RAW_URL.startswith("postgres://") else RAW_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()


def create_initial_admin():
    email = "admin@popote.com"
    password = os.getenv("ADMIN_SETUP_PASSWORD")

    if not password:
        print("❌ Error: Set the password using $env:ADMIN_SETUP_PASSWORD='...'")
        return

    try:
        # 1. Connection Check
        db.execute(text("SELECT 1"))

        # 2. Check if exists
        exists = db.query(models.User).filter(models.User.email == email).first()
        if exists:
            print("Admin already exists!")
            return

        # 3. Native Bcrypt Hashing (Bypasses Passlib bugs)
        hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed_str = hashed_bytes.decode('utf-8')

        # 4. Create User (Matching your exact models.py)
        new_user = models.User(
            email=email,
            password=hashed_str
        )

        db.add(new_user)
        db.commit()
        print(f"✅ SUCCESS: Admin '{email}' created in Render DB.")

    except Exception as e:
        db.rollback()
        print(f"❌ ERROR: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_initial_admin()