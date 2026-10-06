from typing import Literal
from pydantic import BaseModel

class ReviewerSubmissionStatusUpdate(BaseModel):
    status: Literal[
        "unread",
        "backup",
        "accepted",
        "rejected"
    ]