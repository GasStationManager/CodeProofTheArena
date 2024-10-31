from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.core import security
from app.core.config import settings
from app.schemas.token import Token
from app.schemas.user import User, UserCreate


import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register", response_model=User)
def register_user(user: UserCreate, db: Session = Depends(deps.get_db)):
    logger.debug(f"Attempting to register user with email: {user.email}")
    try:
        db_user = crud.user.get_user_by_email(db, email=user.email)
        if db_user:
            logger.info(f"User with email {user.email} already exists")
            raise HTTPException(status_code=400, detail="Email already registered")
        return crud.user.create_user(db=db, user=user)
    except Exception as e:
        logger.error(f"Error during user registration: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/login", response_model=Token)
def login_for_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    user = crud.user.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

