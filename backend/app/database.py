from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()


def _resolve_database_url() -> str:
    # Prefer DATABASE_URL; fallback to SQLALCHEMY_DATABASE_URL for compatibility.
    raw = os.getenv("DATABASE_URL") or os.getenv("SQLALCHEMY_DATABASE_URL")
    if not raw:
        raise ValueError("DATABASE_URL or SQLALCHEMY_DATABASE_URL must be set")

    url = raw.strip().strip('"').strip("'")
    # Some providers expose postgres://; SQLAlchemy prefers postgresql://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


SQLALCHEMY_DATABASE_URL = _resolve_database_url()
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
