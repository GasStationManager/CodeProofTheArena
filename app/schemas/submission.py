from pydantic import BaseModel
from datetime import datetime

class SubmissionBase(BaseModel):
    code: str
    proof: str

class SubmissionCreate(SubmissionBase):
    challenge_id: int

class SubmissionUpdate(SubmissionBase):
    is_correct: bool | None = None
    feedback: str | None = None

class SubmissionInDBBase(SubmissionBase):
    id: int
    challenge_id: int
    user_id: int
    is_correct: bool
    feedback: str | None = None
    submitted_at: datetime

    class Config:
        orm_mode = True

class Submission(SubmissionInDBBase):
    pass

class SubmissionInDB(SubmissionInDBBase):
    pass

class SubmissionResult(BaseModel):
    is_correct: bool
    feedback: str
