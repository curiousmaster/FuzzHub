"""
File: fuzzhub/database/init_db.py

Initialize database tables.
"""

from fuzzhub.database.base import Base
from fuzzhub.database.session import engine


def init_database():
    Base.metadata.create_all(bind=engine)
