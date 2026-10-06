from pydantic import BaseModel, Field

class ReviewerRegisterRequest(BaseModel):
    company_name: str = Field(
        min_length=1,
        max_length=200
    )
    description: str = Field(
        min_length=1,
        max_length=500
    )
    password: str = Field(
        min_length=8,
        max_length=128
    )

class ReviewerLoginRequest(BaseModel):
    company_name: str = Field(
        min_length=1,
        max_length=200
    )
    description: str = Field(
        min_length=1,
        max_length=500
    )
    password: str = Field(
        min_length=8,
        max_length=128
    )

class ReviewerResponse(BaseModel):
    id: int
    company_name: str
    description: str

    model_config = {
        "from_attributes": True
    }