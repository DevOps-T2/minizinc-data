from os import stat
from fastapi import FastAPI, Query, HTTPException
from typing import Optional
import google_storage
import mysql_storage
import models

app = FastAPI()

@app.get('/api/minizinc/upload/', response_model=models.SignedUrl)
def get_signed_upload_url(userID : Optional[int] = Query(None), fileUUID: Optional[str] = Query(None)):
    # If UUID is given, it will create a link for PUT where you can update what is already stored
    # If UUID is not given you will be given a link for PUT where you can create a NEW file.
    if fileUUID and userID:
        if not mysql_storage.file_exists(userID, fileUUID):
            raise HTTPException(status_code=404, detail='File not found.')
        return google_storage.generatePostUrl(fileUUID)
    else:
        return google_storage.generatePostUrl()

@app.post('/api/minizinc/upload/')
def upload_file(file: models.File):
    return mysql_storage.create_file(file)


@app.get('/api/minizinc/{userID}/')
def get_user_files(userID : int):
    if not mysql_storage.user_exists(userID):
        raise HTTPException(status_code=404, detail='User not found.')
    return mysql_storage.get_files(userID)


@app.delete('/api/minizinc/{userID}/')
def delete_user(userID : int):
    files = mysql_storage.get_files(userID)
    for file in files:
        google_storage.delete_file(file.fileUUID)
    # Delete all files for the user from google storage.
    return mysql_storage.delete_files(userID)


@app.get('/api/minizinc/{userID}/{fileUUID}')
def get_file(userID : int, fileUUID : str):
    if not mysql_storage.file_exists(userID, fileUUID):
        raise HTTPException(status_code=404, detail='No such file exists for the given user.')
    return google_storage.generateGetUrl(fileName=fileUUID)


@app.delete('/api/minizinc/{userID}/{fileUUID}')
def delete_file(userID : int, fileUUID : str):
    if not mysql_storage.file_exists(userID, fileUUID):
        raise HTTPException(status_code=404, detail='No such file exists for the given user')
    files = mysql_storage.get_file(userID, fileUUID)
    google_storage.delete_file(fileUUID)
    return mysql_storage.delete_file(userID, fileUUID)



