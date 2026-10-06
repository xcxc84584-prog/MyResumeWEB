from pydantic import BaseModel, Field

class ReviewEnterRequest(BaseModel):
    password: str = Field(
        min_length=8,
        max_length=255
    )

class ReviewExitRequest(BaseModel):
    password: str = Field(
        min_length=8,
        max_length=255
    )