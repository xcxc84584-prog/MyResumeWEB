from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.database import Base

class ReviewerAccount(Base):
    __tablename__ = "reviewer_accounts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    company_name = Column(
        String(200),
        nullable=False,
        index=True
    )

    description = Column(
        String(500),
        nullable=False,
        index=True
    )

    password_hash = Column(
        String(255),
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

    submissions = relationship(
        "ResumeSubmission",
        back_populates="reviewer_account",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint(
            "company_name",
            "description",
            name="uq_reviewer_company_description"
        ),
    )