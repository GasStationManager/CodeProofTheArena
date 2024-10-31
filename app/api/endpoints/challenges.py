from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.post("/", response_model=schemas.Challenge)
def create_challenge(
    challenge: schemas.ChallengeCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.challenge.create_challenge(db=db, challenge=challenge, owner_id=current_user.id)

@router.get("/", response_model=List[schemas.Challenge])
def read_challenges(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db)
):
    challenges = crud.challenge.get_challenges(db, skip=skip, limit=limit)
    return challenges

@router.get("/{challenge_id}", response_model=schemas.Challenge)
def read_challenge(
    challenge_id: int,
    db: Session = Depends(deps.get_db)
):
    db_challenge = crud.challenge.get_challenge(db, challenge_id=challenge_id)
    if db_challenge is None:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return db_challenge

@router.put("/{challenge_id}", response_model=schemas.Challenge)
def update_challenge(
    challenge_id: int,
    challenge: schemas.ChallengeUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    db_challenge = crud.challenge.get_challenge(db, challenge_id=challenge_id)
    if db_challenge is None:
        raise HTTPException(status_code=404, detail="Challenge not found")
    if db_challenge.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud.challenge.update_challenge(db=db, challenge_id=challenge_id, challenge=challenge, owner_id=current_user.id)

@router.delete("/{challenge_id}", response_model=schemas.Challenge)
def delete_challenge(
    challenge_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    db_challenge = crud.challenge.get_challenge(db, challenge_id=challenge_id)
    if db_challenge is None:
        raise HTTPException(status_code=404, detail="Challenge not found")
    if db_challenge.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud.challenge.delete_challenge(db=db, challenge_id=challenge_id, owner_id=current_user.id)

