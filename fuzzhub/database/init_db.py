"""
File: fuzzhub/database/init_db.py
"""

from fuzzhub.database.session import engine
from fuzzhub.database.models import Base


def init_database():
    """
    Create all database tables.
    Safe to call multiple times.
    """
    Base.metadata.create_all(bind=engine)
