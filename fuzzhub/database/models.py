"""
File: fuzzhub/database/models.py

Core database models for FuzzHub.
"""

from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Text,
    Float,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from fuzzhub.database.base import Base


def gen_uuid():
    return str(uuid.uuid4())


# -------------------------------------------------
# Campaign
# -------------------------------------------------

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    target_binary = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    active = Column(Boolean, default=True)

    fuzzers = relationship("FuzzerInstance", back_populates="campaign")
    crashes = relationship("Crash", back_populates="campaign")


# -------------------------------------------------
# Fuzzer Instance
# -------------------------------------------------

class FuzzerInstance(Base):
    __tablename__ = "fuzzer_instances"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    campaign_id = Column(String(36), ForeignKey("campaigns.id"))
    fuzzer_type = Column(String(100), nullable=False)

    pid = Column(Integer, nullable=True)
    state = Column(String(50), nullable=False)

    started_at = Column(DateTime, nullable=True)
    last_heartbeat = Column(DateTime, nullable=True)

    campaign = relationship("Campaign", back_populates="fuzzers")


# -------------------------------------------------
# Crash
# -------------------------------------------------

class Crash(Base):
    __tablename__ = "crashes"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    campaign_id = Column(String(36), ForeignKey("campaigns.id"))

    fuzzer_instance_id = Column(String(36), nullable=True)

    crash_hash = Column(String(128), index=True)
    crash_type = Column(String(255), nullable=True)

    input_path = Column(Text, nullable=True)
    stack_trace = Column(Text, nullable=True)

    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    occurrences = Column(Integer, default=1)

    campaign = relationship("Campaign", back_populates="crashes")


# -------------------------------------------------
# Metrics (Time-Series)
# -------------------------------------------------

class MetricSnapshot(Base):
    __tablename__ = "metric_snapshots"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    fuzzer_instance_id = Column(String(36), nullable=False)

    exec_per_sec = Column(Float, nullable=True)
    corpus_size = Column(Integer, nullable=True)
    coverage = Column(Float, nullable=True)
    crashes_found = Column(Integer, nullable=True)

    timestamp = Column(DateTime, default=datetime.utcnow)


# -------------------------------------------------
# Worker Node (Future Distributed Mode)
# -------------------------------------------------

class WorkerNode(Base):
    __tablename__ = "worker_nodes"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    hostname = Column(String(255), nullable=False)

    last_seen = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="online")
