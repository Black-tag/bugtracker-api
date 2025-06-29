from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sql import Bug, engine, Base
from sqlalchemy.orm import sessionmaker, Session


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()

bugs = Bug()
# dependancy to get a session per request

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()    


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "welcome to bugtracker-api"}




class BugInput(BaseModel):
    title: str
    description: str 


class BugRead(BugInput):
    id: int
    class config:
        orm_mode = True   

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
   
    
