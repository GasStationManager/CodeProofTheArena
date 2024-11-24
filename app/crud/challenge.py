from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, case, and_, or_
from app.models.challenge import Challenge
from app.schemas.challenge import ChallengeCreate, ChallengeUpdate
from app.models.submission import Submission
from app.models.user import User

def get_challenge(db: Session, challenge_id: int):
    return db.query(Challenge).filter(Challenge.id == challenge_id).first()


def get_challenges(db: Session, skip: int = 0, limit: int = 100):
    success_case = case(
        (and_(
            Submission.is_correct.is_(True),
            or_(
                Challenge.theorem2_signature.is_(None),
                Challenge.theorem2_signature == '',
                Submission.is_correct2.is_(True)
            )
        ), 1),
        else_=0
    )

    return (db.query(Challenge,
                    User.display_name.label('creator_name'),
                    func.count(Submission.id).label('total_submissions'),
                    func.coalesce(func.sum(success_case),0).label('successful_submissions')
                    )
            .join(User, Challenge.owner_id == User.id)
            .outerjoin(Submission, Challenge.id == Submission.challenge_id)
            .group_by(Challenge.id, User.id, User.display_name)
            .order_by(Challenge.id)
            .offset(skip)
            .limit(limit)
            .all())

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
    else:
        raise ValueError("Challenge not found")

def delete_challenge(db: Session, challenge_id: int, owner_id: int):
    db_challenge = db.query(Challenge).filter(Challenge.id == challenge_id, Challenge.owner_id == owner_id).first()
    if db_challenge:
        db.delete(db_challenge)
        db.commit()
    return db_challenge

