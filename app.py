from fastapi import FastAPI, Query
from storage import generatePostUrl, generateGetUrl
from pydantic import BaseModel
from typing import Optional

class File(BaseModel):
    userID: int
    fileName: str
    fileUUID: str

app = FastAPI()

@app.get('/api/minizinc/upload/')
def get_signed_upload_url(UUID: Optional[str] = Query(None)):
    # If UUID is given, it will create a link for PUT where you can update what is already stored
    # If UUID is not given you will be given a link for PUT where you can create a NEW file.
    if UUID:
        return generatePostUrl(UUID)
    else:
        return generatePostUrl()

@app.post('/api/minizinc/upload/')
def upload_file(file: File):
    # Need this information stored in the database.
    # Insert file into database.
    return file


@app.get('/api/minizinc/{userID}/')
def get_user_files(userID):
    # Returns all files, i.e. filename and file UUID for a given user.
    return "Yes."


@app.delete('/api/minizinc/{userID}/')
def delete_user(userID):
    # Remove all rows from database
    # Remove all files from google storage
    return f"User: {userID} - deleted!"


@app.get('/api/minizinc/{userID}/{fileUUID}')
def get_file(userID, fileUUID):
    return generateGetUrl(fileName=fileUUID)


@app.delete('/api/minizinc/{userID}/{fileUUID}')
def del_file(userID, fileUUID):
    # Remove row from database.
    # Remove file from google storage
    fileName = "Get filename from database."
    return f"File: {fileName} - deleted!"



