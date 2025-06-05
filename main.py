from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
 


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "welcome to bugtracker-api"}


bugs_db = {
    1: {"id": 1, "title": "Bug 1", "description": "Description of bug 1"},
    2: {"id": 2, "title": "Bug 2", "description": "Description of bug 2"},
}

class BugInput(BaseModel):
    title: str
    description: str 

@app.get("/bugs")
async def get_bugslist():
    return {"bugs": list(bugs_db.values())}


@app.get("/bugs/{bug_id}")
async def get_bug(bug_id: int):
    if bug_id in bugs_db:
        return {"bug": bugs_db[bug_id]}
    raise HTTPException(status_code=404,detail="bug not found")  

@app.post("/bugs")
async def create_bug(bug: BugInput):
    new_id = max(bugs_db.keys(),default=0) + 1
    bugs_db[new_id] = {
        "id" : new_id,
        "title" : bug.title,
        "description" : bug.description
    }
    return bugs_db[new_id]



@app.put("/bugs/{bug_id}")
async def update_bug(bug_id: int,bug: BugInput):
    if bug_id in bugs_db:
        bugs_db[bug_id].update({
        "title" : bug.title,
        "description" : bug.description
    })
    else:
        raise HTTPException(status_code=404,details="bug not found")  

    return bugs_db[bug_id]



@app.delete("/bugs/{bug_id}")
async def delete_bug(bug_id: int):
    if bug_id in bugs_db:
        deleted = bugs_db.pop(bug_id)
    else:
        raise HTTPException(status_code=404,details="bug not found")      
    return {"deleted": deleted }  
