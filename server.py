import os

from fastapi import Body, FastAPI, UploadFile

from authentication import is_admin
from compression import extract

app = FastAPI()

@app.get("/")
async def root():
    return {"flag": os.environ.get("FLAG")}


@app.post("/flag")
async def flag(secret_file: UploadFile, username: str, password: str):
    if is_admin(username, password):
        return {"flag": os.environ.get("FLAG")}
    else:
        return {""}
    return {
        "filename": secret_file.filename,
        "is_admin": is_admin(username, password)
    }
