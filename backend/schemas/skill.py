from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from backend.schemas.document import DocumentSummary

class LearningDuration(str, Enum):
    less_than_30_days = "less_than_30_days"
    one_month = "one_month"
    three_months = "three_months"
    six_months = "six_months"
    over_one_year = "over_one_year"

class ProficiencyLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"

class SkillCreate(BaseModel):
    skill_name: str = Field(
        min_length=1,
        max_length=100
    )
    learning_duration: LearningDuration
    proficiency_level: ProficiencyLevel

class SkillUpdate(BaseModel):
    skill_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )
    learning_duration: LearningDuration | None = None
    proficiency_level: ProficiencyLevel | None = None

class SkillResponse(BaseModel):
    id: int
    skill_name: str
    learning_duration: LearningDuration
    proficiency_level: ProficiencyLevel
    created_at: datetime
    updated_at: datetime
    documents: list[DocumentSummary] = []

    model_config = {
        "from_attributes": True
    }