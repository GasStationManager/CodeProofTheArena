from sqlalchemy.orm import Session
from app.models.challenge import Challenge
from app.schemas.challenge import ChallengeCreate, ChallengeUpdate

def get_challenge(db: Session, challenge_id: int):
    return db.query(Challenge).filter(Challenge.id == challenge_id).first()

def get_challenges(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Challenge).offset(skip).limit(limit).all()

def create_challenge(db: Session, challenge: ChallengeCreate, owner_id: int):
    db_challenge = Challenge(**challenge.dict(), owner_id=owner_id)
    db.add(db_challenge)
    db.commit()
    db.refresh(db_challenge)
    return db_challenge

def update_challenge(db: Session, challenge_id: int, challenge: ChallengeUpdate, owner_id: int):
    db_challenge = db.query(Challenge).filter(Challenge.id == challenge_id, Challenge.owner_id == owner_id).first()
    if db_challenge:
        update_data = challenge.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_challenge, key, value)
        db.commit()
        db.refresh(db_challenge)
    return db_challenge

def delete_challenge(db: Session, challenge_id: int, owner_id: int):
    db_challenge = db.query(Challenge).filter(Challenge.id == challenge_id, Challenge.owner_id == owner_id).first()
    if db_challenge:
        db.delete(db_challenge)
        db.commit()
    return db_challenge

