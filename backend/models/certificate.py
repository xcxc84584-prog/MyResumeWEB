from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base
from backend.models.association import certificate_documents

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    certificate_name = Column(
        String(200),
        nullable=False
    )

    issuer = Column(
        String(200),
        nullable=True
    )

    issue_date = Column(
        Date,
        nullable=True
    )

    expiration_date = Column(
        Date,
        nullable=True
    )

    certificate_number = Column(
        String(100),
        nullable=True
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
        back_populates="certificates"
    )
    documents = relationship(
        "Document",
        secondary=certificate_documents,
        back_populates="certificates"
    )