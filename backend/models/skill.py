from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base
from backend.models.association import skill_documents

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    skill_name = Column(
        String(100),
        nullable=False
    )

    learning_duration = Column(
        String(30),
        nullable=False
    )

    proficiency_level = Column(
        String(30),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="skills"
    )
    documents = relationship(
        "Document",
        secondary=skill_documents,
        back_populates="skills"
    )