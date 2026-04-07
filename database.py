import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Credentials from your NEW screenshot
# Note: The username now includes your project ID (postgres.qvrruys...)
db_user = "postgres.qvrruysjkwhqvkpuodhm"
db_password = "njeru119095@students"
db_host = "aws-0-eu-west-1.pooler.supabase.com"
db_port = 6543
db_name = "postgres"

# 2. Construct URL
connection_url = URL.create(
    drivername="postgresql",
    username=db_user,
    password=db_password,
    host=db_host,
    port=db_port,
    database=db_name,
    query={"sslmode": "require"} # ✅ REQUIRED for the Pooler
)

# 3. Create Engine
# Added pool_pre_ping to keep the connection alive
engine = create_engine(
    connection_url,
    pool_pre_ping=True,
    connect_args={'connect_timeout': 10}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()