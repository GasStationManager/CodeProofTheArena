from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from app.models.submission import Submission
from app.schemas.submission import SubmissionCreate, SubmissionUpdate
from app import crud
from app.services.judge import check_lean_proof

def get_submission(db: Session, submission_id: int):
    return db.query(Submission).options(joinedload(Submission.user), joinedload(Submission.challenge)).filter(Submission.id == submission_id).first()
def get_submissions_by_challenge(db: Session, challenge_id: int, skip: int = 0, limit: int = 100):
    return db.query(Submission).filter(Submission.challenge_id == challenge_id)\
        .options(joinedload(Submission.user))\
        .order_by(desc(Submission.submitted_at))\
        .offset(skip).limit(limit).all()

def get_submissions_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Submission).filter(Submission.user_id == user_id).offset(skip).limit(limit).all()


def create_submission(db: Session, submission: SubmissionCreate, user_id: int):
    db_challenge = crud.challenge.get_challenge(db, challenge_id=submission.challenge_id)
    if not db_challenge:
        raise ValueError("Challenge not found")

    judging_result = check_lean_proof(
        {"function_signature": db_challenge.function_signature, "theorem_signature": db_challenge.theorem_signature, "theorem2_signature":db_challenge.theorem2_signature},
        {"code": submission.code, "proof": submission.proof, "proof2": submission.proof2}
    )

    db_submission = Submission(
        **submission.dict(),
        user_id=user_id,
        is_correct=judging_result["is_correct"],
        is_correct2=judging_result["is_correct2"],
        feedback=judging_result["feedback"],
        feedback2=judging_result["feedback2"]
    )
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission

def update_submission(db: Session, submission_id: int, submission: SubmissionUpdate):
    db_submission = get_submission(db, submission_id)
    if db_submission:
        update_data = submission.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_submission, key, value)
        db.commit()
        db.refresh(db_submission)
    return db_submission

