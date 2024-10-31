from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.post("/", response_model=schemas.Submission)
def create_submission(
    submission: schemas.SubmissionCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return crud.submission.create_submission(db=db, submission=submission, user_id=current_user.id)

@router.get("/challenge/{challenge_id}", response_model=List[schemas.Submission])
def read_submissions_by_challenge(
    challenge_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
):
    submissions = crud.submission.get_submissions_by_challenge(db, challenge_id=challenge_id, skip=skip, limit=limit)
    return submissions

@router.get("/user/me", response_model=List[schemas.Submission])
def read_user_submissions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    submissions = crud.submission.get_submissions_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return submissions

@router.get("/{submission_id}", response_model=schemas.Submission)
def read_submission(
    submission_id: int,
    db: Session = Depends(deps.get_db),
):
    submission = crud.submission.get_submission(db, submission_id=submission_id)
    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission

@router.get("/{submission_id}/result", response_model=schemas.SubmissionResult)
def read_submission_result(
    submission_id: int,
    db: Session = Depends(deps.get_db)
):
    submission = crud.submission.get_submission(db, submission_id=submission_id)
    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    return {"is_correct": submission.is_correct}
