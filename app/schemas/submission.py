from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SubmissionBase(BaseModel):
    code: str
    proof: str
    proof2: Optional[str] = None

class SubmissionCreate(SubmissionBase):
    challenge_id: int

class SubmissionUpdate(SubmissionBase):
    is_correct: bool | None = None
    is_correct2: bool | None = None
    feedback: str | None = None
    feedback2: str | None = None

class SubmissionInDBBase(SubmissionBase):
    id: int
    challenge_id: int
    user_id: int
    is_correct: bool
    is_correct2: Optional[bool]
    feedback: str | None = None
    feedback2: str | None = None
    submitted_at: datetime

    class Config:
        orm_mode = True

class Submission(SubmissionInDBBase):
    pass

class SubmissionInDB(SubmissionInDBBase):
    pass

class SubmissionResult(BaseModel):
    is_correct: bool
    is_correct2: Optional[bool]
    feedback: str
    feedback2: Optional[str]
