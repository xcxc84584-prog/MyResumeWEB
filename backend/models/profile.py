from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.database import Base

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
        index=True
    )

    avatar_path = Column(String(500), nullable=True)
    full_name = Column(String(100), nullable=False)
    gender = Column(String(30), nullable=True)
    marital_status = Column(String(30), nullable=True)
    birth_date = Column(Date, nullable=True)
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    blood_type = Column(String(30), nullable=True)
    phone = Column(String(30), nullable=True)
    address = Column(String(500), nullable=True)
    education_level = Column(String(50), nullable=True)
    medical_history = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="profile"
    )