from pydantic import BaseModel, EmailStr


# Models
class User(BaseModel):
    username: str
    fullname: str
    email: EmailStr
    disabled: bool

class UserDB(User):
    password: str


# Custom exceptions
class UserAlreadyExistsError(Exception):
    pass

class UserNotFoundError(Exception):
    pass

class IncorrectPasswordError(Exception):
    pass
