import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Credentials from your Render screenshot
# Note: For local testing, use the 'External Database URL' from Render.
# When deployed, Render handles this via the DATABASE_URL environment variable.
DB_USER = "popote_db_user"
DB_PASS = "K2nqesEpjHdreV68AjuHKAImjaSycaB2"
DB_HOST = "dpg-d7bvc61j2pic739u0lu0-a" # Internal host for Render
DB_NAME = "popote_db"
DB_PORT = "5432"

# 2. Construct the URL
# We prioritize the system environment variable 'DATABASE_URL' which Render provides
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Fallback for local development
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Render/SQLAlchemy Fix:
# Render provides URLs starting with 'postgres://', but SQLAlchemy requires 'postgresql://'
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 3. Create Engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True, # Checks connection health before using it
    connect_args={'connect_timeout': 10}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()