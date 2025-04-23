import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use DATABASE_URL from env, fallback to local dev DB
DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres123@localhost:5432/caradvisor_db"
)

engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
