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
            raise HTTPException(status_code=404, detail='There does not exist a file with the given identifier')
        return google_storage.generatePostUrl(fileUUID)
    else:
        return google_storage.generatePostUrl()

@app.post('/api/minizinc/upload/')
def upload_file(file: models.File):
    if not google_storage.file_exists(file.fileUUID):
        return HTTPException(status_code=400, detail='No such file found in storage')
    if mysql_storage.file_exists(file.userID, file.fileUUID):
        return HTTPException(status_code=400, detail='File already exists!')
    mysql_storage.create_file(file)
    return "File uploaded!"


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
    row_count = mysql_storage.delete_files(userID)
    return f'Success! - ${row_count} file(s) deleted'


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
    row_count = mysql_storage.delete_file(userID, fileUUID)
    return 'Success! - ${row_count} file(s) deleted'