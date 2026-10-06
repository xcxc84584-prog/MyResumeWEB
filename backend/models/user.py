from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False
    )
    profile = relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    skills = relationship(
        "Skill",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    certificates = relationship(
        "Certificate",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    documents = relationship(
        "Document",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    resume_submissions = relationship(
        "ResumeSubmission",
        back_populates="applicant",
        cascade="all, delete-orphan"
    )
    account_mode = Column(
        String(20),
        nullable=False,
        default="edit"
    )