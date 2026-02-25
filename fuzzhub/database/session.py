"""
File: fuzzhub/database/session.py

Database engine and session factory.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fuzzhub.utils.config import get_config

cfg = get_config()

DATABASE_URL = cfg["database"]["url"]

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
