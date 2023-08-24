from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import usersdb as db
from jose import jwt, JWTError
from datetime import datetime, timedelta
from schemas import User, UserNotFoundError, IncorrectPasswordError


ALGORITHM = "HS256"
SECRET = "Secret"
TOKEN_DURATION = 5

router = APIRouter(tags=["Auth"])
oauth = OAuth2PasswordBearer(tokenUrl="login")


# Dependencies criteria
async def auth_user(token: str = Depends(oauth)):
    try:
        username = jwt.decode(token, SECRET, algorithms=[ALGORITHM]).get("sub")
        if username is None:
            raise HTTPException(detail="Invalid credentials", status_code=401)
    except JWTError:
        raise HTTPException(detail="Invalid credentials", status_code=401)
    return db.get_user(username)


async def current_user(user: User = Depends(auth_user)):
    if user.disabled:
        raise HTTPException(detail="User disabled", status_code=400)
    return user


def create_token(username: str):
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(minutes=TOKEN_DURATION)
    }
    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)
    return token


@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    try:
        user = db.get_auth_user(form.username, form.password)
    except UserNotFoundError:
        raise HTTPException(detail="This user doesn't exist", status_code=400)
    except IncorrectPasswordError:
        raise HTTPException(detail="Wrong password", status_code=400)
    return {"access_token": create_token(user.username),
            "token_type": "bearer"}


@router.get("/users/me")
async def me(user: User = Depends(current_user)):
    return user

# Need to generate a refresh token when the access token expires
# Need to make more secure the jwt encode key