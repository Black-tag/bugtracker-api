from pydantic import BaseModel




class BugInput(BaseModel):
    title: str
    description: str 


class BugRead(BugInput):
    id: int
    class Config:
        orm_mode = True 



class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserCreate(BaseModel):
    username: str
    password: str

class UserRead(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True