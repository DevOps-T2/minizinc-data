from os import stat
from fastapi import FastAPI, Query, HTTPException
import google_storage
import mysql_storage
from typing import Optional
from models import File

app = FastAPI()

@app.get('/api/minizinc/upload/')
def get_signed_upload_url(userID, fileUUID: Optional[str] = Query(None)):
    # If UUID is given, it will create a link for PUT where you can update what is already stored
    # If UUID is not given you will be given a link for PUT where you can create a NEW file.
    if fileUUID:
        if not mysql_storage.file_exists(userID, fileUUID):
            raise HTTPException(status_code=404, detail='File not found.')
        return google_storage.generatePostUrl(fileUUID)
    else:
        return google_storage.generatePostUrl()

@app.post('/api/minizinc/upload/')
def upload_file(file: File):
    return mysql_storage.create_file(file)


@app.get('/api/minizinc/{userID}/')
def get_user_files(userID):
    if not mysql_storage.user_exists(userID):
        raise HTTPException(status_code=404, detail='User not found.')
    return mysql_storage.get_files(userID)


@app.delete('/api/minizinc/{userID}/')
def delete_user(userID):
    # Delete all files for the user from google storage.
    return mysql_storage.delete_files(userID)


@app.get('/api/minizinc/{userID}/{fileUUID}')
def get_file(userID, fileUUID):
    if not mysql_storage.file_exists(userID, fileUUID):
        raise HTTPException(status_code=404, detail='No such file exists for the given user.')
    return google_storage.generateGetUrl(fileName=fileUUID)


@app.delete('/api/minizinc/{userID}/{fileUUID}')
def delete_file(userID, fileUUID):
    if not mysql_storage.file_exists(userID, fileUUID):
        raise HTTPException(status_code=404, detail='No such file exists for the given user')
    files = mysql_storage.get_file(userID, fileUUID)
    # Need to remove the files from google storage
    return mysql_storage.delete_file(userID, fileUUID)



