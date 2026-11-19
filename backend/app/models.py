from datetime import datetime
from sqlalchemy import (Column, BigInteger, String, Boolean, DateTime,
                        Float, Enum, ForeignKey, Text, JSON)
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(190), unique=True, nullable=False, index=True)
    full_name = Column(String(190), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum("admin", "student", "teacher", name="role_enum"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    scans = relationship("Scan", back_populates="user")
    reports = relationship("Report", back_populates="user", foreign_keys="Report.user_id")

class Scan(Base):
    __tablename__ = "scans"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    url = Column(String(2048), nullable=False)
    domain = Column(String(255), nullable=False)
    status = Column(Enum("safe", "suspicious", "phishing", name="status_enum"), nullable=False)
    category = Column(String(40), nullable=True)
    confidence = Column(Float, nullable=True)
    reasons = Column(JSON, nullable=True)
    source = Column(Enum("extension", "dashboard", name="source_enum"), default="extension")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="scans")

class Report(Base):
    __tablename__ = "reports"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    url = Column(String(2048), nullable=False)
    category = Column(String(40), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum("pending", "verified", "rejected", "false_positive",
                         name="report_status_enum"), default="pending")
    reviewer_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    review_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="reports", foreign_keys=[user_id])

class SiteList(Base):
    __tablename__ = "site_list"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    domain = Column(String(255), unique=True, nullable=False)
    list_type = Column(Enum("trusted", "blocked", name="list_enum"), nullable=False)
    added_by = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(190), nullable=False)
    body = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
