from fastapi import FastAPI, Query, HTTPException, APIRouter, Request
from fastapi.param_functions import Header
from fastapi.params import Depends
from typing import Optional
import google_storage
import mysql_storage
import info
import models

UPLOAD_URL = '/api/minizinc/upload'

app = FastAPI(
    title=info.TITLE,
    version=info.VERSION,
    description=info.DESCRIPTION,
    openapi_tags=info.TAGS_METADATA
)
router = APIRouter()

# Had to include double route with and without trailing backslash to please the gateway-gods
# See: https://github.com/tiangolo/fastapi/issues/2060
@router.get(UPLOAD_URL, response_model=models.SignedUrl, include_in_schema=False)
@router.get(f'{UPLOAD_URL}/', response_model=models.SignedUrl, tags=[info.UPLOAD['name']])
def get_signed_upload_url(req : Request, userID : Optional[str] = Query(None), fileUUID: Optional[str] = Query(None)):
    if fileUUID and userID:
        header_userID = req.headers.get('userid')
        if header_userID != userID:
            raise HTTPException(status_code=401, detail='Unauthorized')
        if not mysql_storage.file_exists(userID, fileUUID):
            raise HTTPException(status_code=404, detail='There does not exist a file with the given identifier')
        return google_storage.generatePostUrl(fileUUID)
    else:
        return google_storage.generatePostUrl()


@router.post('/api/minizinc/upload', include_in_schema=False)
@router.post('/api/minizinc/upload/', tags=[info.UPLOAD['name']])
def upload_file(file: models.File, req : Request):
    if req.headers.get('userid') != file.userID:
        raise HTTPException(status_code=401, detail='Unauthorized')
    if not google_storage.file_exists(file.fileUUID):
        return HTTPException(status_code=400, detail='No such file found in storage')
    if mysql_storage.file_exists(file.userID, file.fileUUID):
        mysql_storage.update_file(file)
        return "File Updated!"
    mysql_storage.create_file(file)
    return "File uploaded!"


@router.get('/api/minizinc/{userID}', include_in_schema=False)
@router.get('/api/minizinc/{userID}/', tags=[info.FILES['name']])
def get_user_files(userID : str, req : Request):
    if req.headers.get('userid') != userID:
        raise HTTPException(status_code=401, detail='Unauthorized')
    if not mysql_storage.user_exists(userID):
        # No user files found
        return []
    return mysql_storage.get_files(userID)


@router.delete('/api/minizinc/{userID}', include_in_schema=False)
@router.delete('/api/minizinc/{userID}/', tags=[info.FILES['name']])
def delete_user(userID : str, req : Request):
    if req.headers.get('role') != 'admin':
        raise HTTPException(status_code=401, detail='Unauthorized')
    files = mysql_storage.get_files(userID)
    for file in files:
        google_storage.delete_file(file.fileUUID)
    # Delete all files for the user from google storage.
    row_count = mysql_storage.delete_files(userID)
    return f'Success! - {row_count} file(s) deleted'


@router.get('/api/minizinc/{userID}/{fileUUID}', include_in_schema=False)
@router.get('/api/minizinc/{userID}/{fileUUID}/', tags=[info.FILES['name']])
def get_file(userID : str, fileUUID : str, req : Request):
    if req.headers.get('userid') != userID:
        raise HTTPException(status_code=401, detail='Unauthorized')
    if not mysql_storage.file_exists(userID, fileUUID):
        raise HTTPException(status_code=404, detail='No such file exists for the given user.')
    return google_storage.generateGetUrl(fileName=fileUUID)


@router.delete('/api/minizinc/{userID}/{fileUUID}', include_in_schema=False)
@router.delete('/api/minizinc/{userID}/{fileUUID}/', tags=[info.FILES['name']])
def delete_file(userID : str, fileUUID : str, req : Request):
    if req.headers.get('userid') != userID:
        raise HTTPException(status_code=401, detail='Unauthorized')
    if not mysql_storage.file_exists(userID, fileUUID):
        raise HTTPException(status_code=404, detail='No such file exists for the given user')
    files = mysql_storage.get_file(userID, fileUUID)
    google_storage.delete_file(fileUUID)
    row_count = mysql_storage.delete_file(userID, fileUUID)
    return 'Success! - {row_count} file(s) deleted'


app.include_router(router)