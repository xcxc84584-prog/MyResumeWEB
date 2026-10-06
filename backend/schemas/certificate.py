from datetime import date, datetime
from pydantic import BaseModel, Field, model_validator
from backend.schemas.document import DocumentSummary

class CertificateCreate(BaseModel):
    certificate_name: str = Field(min_length=1, max_length=200)
    issuer: str | None = Field(default=None, max_length=200)
    issue_date: date | None = None
    expiration_date: date | None = None
    certificate_number: str | None = Field(default=None, max_length=100)

    @model_validator(mode="after")
    def validate_dates(self):
        if (
            self.issue_date is not None
            and self.expiration_date is not None
            and self.expiration_date < self.issue_date
        ):
            raise ValueError(
                "expiration_date cannot be earlier than issue_date"
            )
        return self

class CertificateUpdate(BaseModel):
    certificate_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200
    )
    issuer: str | None = Field(default=None, max_length=200)
    issue_date: date | None = None
    expiration_date: date | None = None
    certificate_number: str | None = Field(default=None, max_length=100)

class CertificateResponse(BaseModel):
    id: int
    certificate_name: str
    issuer: str | None
    issue_date: date | None
    expiration_date: date | None
    certificate_number: str | None
    created_at: datetime
    updated_at: datetime
    documents: list[DocumentSummary] = []

    model_config = {
        "from_attributes": True
    }