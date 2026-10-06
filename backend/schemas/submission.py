from pydantic import BaseModel

class ResumeSubmissionCreate(BaseModel):
    reviewer_account_id: int