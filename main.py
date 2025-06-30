from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from fastapi import FastAPI, HTTPException, Depends,status
from pydantic import BaseModel
from sql import Bug, engine, Base, fake_users_db
from models import BugInput, BugRead, User, UserInDB, Token, TokenData
from sqlalchemy.orm import sessionmaker, Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

bugs = Bug()
# dependancy to get a session per request

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()    


app = FastAPI()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)



def fake_hash_password(password: str):
    return "fakehashed" + password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def authenticate_user(fake_db, username: str, password: str):
    # for production app we will use this when we include a database 
    # user = get_user(fake_db, username)
    # if not user:
    #     return False
    # if not verify_password(password, user.hashed_password):
    #     return False
    # return user
    # fro testing we will using the fakehashed methode
    user = get_user(fake_db, username)
    if not user:
        return False
    if not user.hashed_password == fake_hash_password(password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



@app.get("/")
async def root():
    return {"message": "welcome to bugtracker-api"}



def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}


def fake_decode_token(token):
    user = get_user(fake_users_db, token)
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invaid authentication credentials",
            headers={"WWW-AUTHENTICATE": "Bearer"},
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
    ):
        if current_user.disabled:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm,Depends()]) -> Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
         detail="incorrect username or password",
         headers={"WWW-Authenticate": "Bearer"},
         )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")



@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
    ):
    return current_user 

@app.get("/bugs",response_model=list[BugRead])
async def get_bugslist(db : Session = Depends(get_db)):
    return db.query(Bug).all()
   
    


@app.get("/bugs/{bug_id}",response_model=BugRead)
async def get_bug(bug_id: int ,db : Session = Depends(get_db)):
    bug = db.query(Bug).filter(Bug.id == bug_id).first()
    if not bug:
        raise HTTPException(status_code=404,detail="Bug not found")
    return bug 
    
@app.post("/bugs",response_model=BugRead)
async def create_bug(bug: BugInput,db: Session = Depends(get_db)):
    db_bug = Bug(title=bug.title,description=bug.description)
    db.add(db_bug)
    db.commit()
    db.refresh(db_bug)
    return db_bug
    
    



@app.put("/bugs/{bug_id}",response_model=BugRead)
async def update_bug(bug_id: int,bug: BugInput, db: Session = Depends(get_db)):
    db_bug = db.query(Bug).filter(Bug.id == bug_id).first()
    if not db_bug:
        raise HTTPException(status_code=404, detail="Bug not Found")
    db_bug.title = bug.title
    db_bug.description = bug.description
    db.commit()
    db.refresh(db_bug)
    return db_bug
    
    



@app.delete("/bugs/{bug_id}")
async def delete_bug(bug_id: int,db: Session = Depends(get_db)):
    db_bug = db.query(Bug).filter(Bug.id == bug_id).first()
    if not db_bug:
        raise HTTPException(status_code=404, detail="Bug not Found")
    db.delete(db_bug)
    db.commit()
    return {"detail": "bug deleted"}
   
    
