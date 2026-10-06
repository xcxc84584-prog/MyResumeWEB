from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel, Field

class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"
    prefer_not_to_say = "prefer_not_to_say"

class MaritalStatus(str, Enum):
    single = "single"
    married = "married"
    other = "other"
    prefer_not_to_say = "prefer_not_to_say"

class BloodType(str, Enum):
    a = "A"
    b = "B"
    ab = "AB"
    o = "O"
    unknown = "unknown"
    prefer_not_to_say = "prefer_not_to_say"

class EducationLevel(str, Enum):
    high_school = "high_school"
    vocational_school = "vocational_school"
    associate = "associate"
    bachelor = "bachelor"
    master = "master"
    doctorate = "doctorate"
    other = "other"

class ProfileCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)
    gender: Gender | None = None
    marital_status: MaritalStatus | None = None
    birth_date: date | None = None
    height_cm: float | None = Field(default=None, gt=0, le=300)
    weight_kg: float | None = Field(default=None, gt=0, le=500)
    blood_type: BloodType | None = None
    phone: str | None = Field(default=None, max_length=30)
    address: str | None = Field(default=None, max_length=500)
    education_level: EducationLevel | None = None
    medical_history: str | None = None

class ProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=100)
    gender: Gender | None = None
    marital_status: MaritalStatus | None = None
    birth_date: date | None = None
    height_cm: float | None = Field(default=None, gt=0, le=300)
    weight_kg: float | None = Field(default=None, gt=0, le=500)
    blood_type: BloodType | None = None
    phone: str | None = Field(default=None, max_length=30)
    address: str | None = Field(default=None, max_length=500)
    education_level: EducationLevel | None = None
    medical_history: str | None = None

class ProfileResponse(BaseModel):
    id: int
    full_name: str
    gender: Gender | None
    marital_status: MaritalStatus | None
    birth_date: date | None
    age: int | None
    height_cm: float | None
    weight_kg: float | None
    blood_type: BloodType | None
    phone: str | None
    address: str | None
    education_level: EducationLevel | None
    medical_history: str | None
    avatar_path: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }