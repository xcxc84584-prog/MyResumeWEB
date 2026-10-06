from sqlalchemy import Table, Column, Integer, ForeignKey
from backend.database import Base

skill_documents = Table(
    "skill_documents",
    Base.metadata,
    Column(
        "skill_id",
        Integer,
        ForeignKey(
            "skills.id",
            ondelete="CASCADE"
        ),
        primary_key=True
    ),
    Column(
        "document_id",
        Integer,
        ForeignKey(
            "documents.id",
            ondelete="CASCADE"
        ),
        primary_key=True
    )
)

certificate_documents = Table(
    "certificate_documents",
    Base.metadata,
    Column(
        "certificate_id",
        Integer,
        ForeignKey(
            "certificates.id",
            ondelete="CASCADE"
        ),
        primary_key=True
    ),
    Column(
        "document_id",
        Integer,
        ForeignKey(
            "documents.id",
            ondelete="CASCADE"
        ),
        primary_key=True
    )
)