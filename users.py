from fastapi import APIRouter, HTTPException
import usersdb as db
from schemas import UserDB, UserAlreadyExistsError


router = APIRouter(tags=["User"])


# Endpoints
@router.get("/hello")
async def users():
    return {"message": "hello users"}


# Sign in (add user to database)
@router.post("/signin", status_code=201)
async def signin(user: UserDB):
    try:
        db.add_user(user)
    except UserAlreadyExistsError:
        raise HTTPException(detail="This username already exists", status_code=400)
    return {"message": "signed up successfully"}


# Get all users from database
@router.get("/users", status_code=200)
async def get_users():
    return db.get_users()