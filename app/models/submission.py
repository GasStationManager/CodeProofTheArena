from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    challenge_id = Column(Integer, ForeignKey("challenges.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    code = Column(Text)
    proof = Column(Text)
    proof2 = Column(Text, nullable=True)
    is_correct = Column(Boolean, default=False)
    is_correct2 = Column(Boolean, default=False)
    feedback = Column(Text)
    feedback2 = Column(Text, nullable=True)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    challenge = relationship("Challenge", back_populates="submissions")
    user = relationship("User", back_populates="submissions")

