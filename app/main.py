import logging
from fastapi import FastAPI, Request, Depends, HTTPException, status, Form
#from app.api.api import api_router


from fastapi.responses import RedirectResponse

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.endpoints import auth, challenges, submissions
from app.api import deps
from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.schemas.user import UserCreate
from app.schemas.challenge import ChallengeCreate
from app.models import User

from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
import urllib

app = FastAPI(title="Lean 4 Coding Challenge Website")

# Configure logging
logging.basicConfig(
    #level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Add SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(challenges.router, prefix="/api/challenges", tags=["challenges"])

app.include_router(submissions.router, prefix="/api/submissions", tags=["submissions"])

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")




#app.include_router(api_router)

# Frontend routes

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(deps.get_db)):
    user = crud.user.authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"})
    access_token = security.create_access_token(user.id)
    request.session["token"] = access_token
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

@app.get("/logout")
async def logout(request: Request):
    request.session.pop("token", None)
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)





# Add a custom dependency to get the current user
async def get_current_user(request: Request, db: Session = Depends(deps.get_db)):
    token = request.session.get("token")
    if not token:
        return None
    try:
        payload = security.decode_access_token(token)
        user = crud.user.get_user(db, user_id=payload["sub"])
        return user
    except:
        return None


# Update other routes to use the get_current_user dependency
@app.get("/")
async def home(request: Request, current_user: dict = Depends(get_current_user)):
    return templates.TemplateResponse("index.html", {"request": request, "user": current_user})

@app.get("/challenges")
async def challenges_page(request: Request, db: Session = Depends(deps.get_db), current_user: dict = Depends(get_current_user)):
    challenges_data = crud.challenge.get_challenges(db)
    #print(f"Found {len(challenges)} challenges") 
    return templates.TemplateResponse("challenges.html", {"request": request, "challenges_data": challenges_data, "user": current_user})

@app.get("/challenges/create")
async def create_challenge_page(request: Request, current_user: User = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("create_challenge.html", {"request": request, "user": current_user})

@app.post("/challenges/create")
async def create_challenge(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    function_signature: str = Form(...),
    theorem_signature: str = Form(...),
    theorem2_signature: str = Form(None),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    try:
        if 'import' not in function_signature:
            function_signature = 'import Mathlib\n\n' + function_signature

        challenge = ChallengeCreate(
            title=title,
            description=description,
            function_signature=function_signature,
            theorem_signature=theorem_signature,
            theorem2_signature=theorem2_signature
        )
        new_challenge = crud.challenge.create_challenge(db, challenge=challenge, owner_id=current_user.id)
    except ValueError as e:
        return templates.TemplateResponse("create_challenge.html", {"request": request, "user": current_user, "error": str(e)})
    
    return RedirectResponse(url=f"/challenges/{new_challenge.id}", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/challenges/{challenge_id}")
async def challenge_detail(
    request: Request, 
    challenge_id: int, 
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(get_current_user)
):
    challenge = crud.challenge.get_challenge(db, challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    code = 'import Mathlib\n\n' if  'import' not in challenge.function_signature else ''
    code+= challenge.function_signature+'\n\n'+challenge.theorem_signature
    if challenge.theorem2_signature:
        code+='\n\n'+ challenge.theorem2_signature
    return templates.TemplateResponse(
        "challenge_detail.html", 
        {"request": request, "challenge": challenge, "code": urllib.parse.quote(code), "user": current_user}
    )

@app.post("/challenges/{challenge_id}")
async def submit_challenge(
    request: Request,
    challenge_id: int,
    code: str = Form(...),
    proof: str = Form(...),
    proof2: str = Form(None),
    session_token: str = Form(...),
    db: Session = Depends(deps.get_db)
):
    logger.debug(f"Session token: {session_token[:10]}...") 
    if not session_token:
        logger.warning("No session token provided")
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    try:
        payload = security.decode_access_token(session_token)
        user = crud.user.get_user(db, user_id=payload["sub"])
        if not user:
            logger.warning(f"No user found for token payload: {payload}")
            return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        logger.error(f"Error decoding token: {str(e)}")
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    challenge = crud.challenge.get_challenge(db, challenge_id=challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    # Require proof2 if challenge has theorem2_signature
    if challenge.theorem2_signature and not proof2:
        return templates.TemplateResponse(
            "challenge_detail.html",
            {
                "request": request,
                "challenge": challenge,
                "user": current_user,
                "error": "Second proof is required for this challenge"
            }
        )

    submission = schemas.SubmissionCreate(challenge_id=challenge_id, code=code, proof=proof, proof2=proof2)
    try:
        crud.submission.create_submission(db=db, submission=submission, user_id=user.id)
        logger.info('finished creating submission')
        return RedirectResponse(url=f"/challenges/{challenge_id}/submissions", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        # Log the error
        print(f"Error creating submission: {str(e)}")
        return templates.TemplateResponse(
            "challenge_detail.html", 
            {"request": request, "challenge": crud.challenge.get_challenge(db, challenge_id), "user": user, "error": "An error occurred while submitting. Please try again."}
        )

@app.get("/challenges/{challenge_id}/edit")
async def edit_challenge_page(
    request: Request,
    challenge_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    challenge = crud.challenge.get_challenge(db, challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    if challenge.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this challenge")
    
    return templates.TemplateResponse(
        "edit_challenge.html",
        {
            "request": request,
            "challenge": challenge,
            "user": current_user
        }
    )

@app.post("/challenges/{challenge_id}/edit")
async def edit_challenge(
    request: Request,
    challenge_id: int,
    title: str = Form(...),
    description: str = Form(...),
    function_signature: str = Form(...),
    theorem_signature: str = Form(...),
    theorem2_signature: str = Form(None),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    challenge = crud.challenge.get_challenge(db, challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    if challenge.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this challenge")
    
    try:
        updated_challenge = crud.challenge.update_challenge(
            db,
            challenge_id=challenge_id,
            challenge=schemas.ChallengeUpdate(
                title=title,
                description=description,
                function_signature=function_signature,
                theorem_signature=theorem_signature,
                theorem2_signature=theorem2_signature if theorem2_signature else None
            )
        )
    except ValueError as e:
        return templates.TemplateResponse(
            "edit_challenge.html",
            {
                "request": request,
                "challenge": challenge,
                "user": current_user,
                "error": str(e)
            }
        )
    
    return RedirectResponse(url=f"/challenges/{challenge_id}", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/challenges/{challenge_id}/submissions")
async def challenge_submissions(
    request: Request,
    challenge_id: int,
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(get_current_user)
):
    challenge = crud.challenge.get_challenge(db, challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    skip = (page - 1) * per_page
    submissions = crud.submission.get_submissions_by_challenge(db, challenge_id, skip=skip, limit=per_page)
    
    return templates.TemplateResponse(
        "challenge_submissions.html",
        {
            "request": request,
            "challenge": challenge,
            "submissions": submissions,
            "page": page,
            "per_page": per_page,
            "user": current_user
        }
    )

@app.get("/submissions/{submission_id}")
async def submission_detail(
    request: Request,
    submission_id: int,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(get_current_user)
):
    submission = crud.submission.get_submission(db, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return templates.TemplateResponse(
        "submission_detail.html",
        {
            "request": request,
            "submission": submission,
            "user": current_user
        }
    )


@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(
    request: Request,
    email: str = Form(...),
    display_name: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(deps.get_db)
):
    if password != confirm_password:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Passwords do not match"})
    
    try:
        user = UserCreate(email=email, display_name=display_name, password=password)
        crud.user.create_user(db, user)
    except ValueError as e:
        return templates.TemplateResponse("register.html", {"request": request, "error": str(e)})
    
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)




