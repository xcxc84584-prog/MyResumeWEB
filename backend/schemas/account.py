from typing import Literal
from pydantic import BaseModel, Field

class AccountDeletionRequest(BaseModel):
    password: str = Field(min_length=1, max_length=1024)
    confirmation: Literal["註銷"]
