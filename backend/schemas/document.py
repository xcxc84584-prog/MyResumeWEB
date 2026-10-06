from datetime import datetime
from pydantic import BaseModel

class DocumentSummary(BaseModel):
    id: int
    original_filename: str
    content_type: str
    file_size: int

    model_config = {
        "from_attributes": True
    }

class DocumentResponse(BaseModel):
    id: int
    original_filename: str
    stored_filename: str
    content_type: str
    file_size: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }