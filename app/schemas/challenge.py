from pydantic import BaseModel
from typing import Optional

class ChallengeBase(BaseModel):
    title: str
    description: str
    function_signature: str
    theorem_signature: str
    theorem2_signature: Optional[str] = None

class ChallengeCreate(ChallengeBase):
    pass

class ChallengeUpdate(ChallengeBase):
    pass

class ChallengeInDBBase(ChallengeBase):
    id: int
    owner_id: Optional[int] = None
    class Config:
        orm_mode = True

class Challenge(ChallengeInDBBase):
    pass

class ChallengeInDB(ChallengeInDBBase):
    pass

