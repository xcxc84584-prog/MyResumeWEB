from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    UniqueConstraint
)
from sqlalchemy.orm import relationship
from backend.database import Base

class ResumeSubmission(Base):
    __tablename__ = "resume_submissions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    applicant_user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    reviewer_account_id = Column(
        Integer,
        ForeignKey(
            "reviewer_accounts.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    status = Column(
        String(30),
        nullable=False,
        default="unread",
        index=True
    )

    resume_snapshot = Column(
        Text,
        nullable=False
    )

    submitted_at = Column(
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

    applicant = relationship(
        "User",
        back_populates="resume_submissions"
    )

    reviewer_account = relationship(
        "ReviewerAccount",
        back_populates="submissions"
    )

    __table_args__ = (
        UniqueConstraint(
            "applicant_user_id",
            "reviewer_account_id",
            name="uq_applicant_reviewer_submission"
        ),
    )