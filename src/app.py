from fastapi import FastAPI, Query, HTTPException, APIRouter, Request, Response, status
from typing import Optional
from typing import List


import google_storage
import mysql_storage
import info
import models

print("test")

UPLOAD_URL = '/api/minizinc/upload'
SYS_ID = 'system'

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
def get_signed_upload_url(req : Request, res : Response, userID : Optional[str] = Query(None), fileUUID: Optional[str] = Query(None)):
    if fileUUID and userID:
        header_userID = req.headers.get('userid')
        if header_userID != userID and header_userID != SYS_ID:
            raise HTTPException(status_code=401, detail='Unauthorized')
        if not mysql_storage.file_exists(userID, fileUUID):
            res.status_code = status.HTTP_200_OK
            return "No file to generate update link for"
        return google_storage.generatePostUrl(fileUUID)
    else:
        return google_storage.generatePostUrl()


@router.post('/api/minizinc/upload', include_in_schema=False)
@router.post('/api/minizinc/upload/', tags=[info.UPLOAD['name']])
def upload_file(file: models.File, req : Request, res : Response):
    header_userID = req.headers.get('userid')
    if header_userID != file.userID and header_userID != SYS_ID:
        raise HTTPException(status_code=401, detail='Unauthorized')
    if not google_storage.file_exists(file.fileUUID):
        res.status_code = status.HTTP_200_OK
        return "No file to update"
    if mysql_storage.file_exists(file.userID, file.fileUUID):
        mysql_storage.update_file(file)
        return "File Updated!"
    mysql_storage.create_file(file)
    return "File uploaded!"


@router.get('/api/minizinc/{userID}', include_in_schema=False)
@router.get('/api/minizinc/{userID}/', tags=[info.FILES['name']], response_model=List[models.File])
def get_user_files(userID : str, req : Request, res : Response):
    header_userID = req.headers.get('userid')
    if header_userID != userID and header_userID != SYS_ID:
        raise HTTPException(status_code=401, detail='Unauthorized')
    if not mysql_storage.user_exists(userID):
        res.status_code = status.HTTP_200_OK
        return []
    return mysql_storage.get_files(userID)


@router.delete('/api/minizinc/{userID}', include_in_schema=False)
@router.delete('/api/minizinc/{userID}/', tags=[info.FILES['name']])
def delete_user(userID : str, req : Request, res : Response):
    if req.headers.get('role') != 'admin':
        raise HTTPException(status_code=403, detail='Forbidden')
    files = mysql_storage.get_files(userID)
    for file in files:
        google_storage.delete_file(file.fileUUID)
    # Delete all files for the user from google storage.
    row_count = mysql_storage.delete_files(userID)
    if row_count == 0:
        res.status_code = status.HTTP_200_OK
        return "No files were deleted"
    return f'Success! - {row_count} file(s) deleted'


@router.get('/api/minizinc/{userID}/{fileUUID}', include_in_schema=False)
@router.get('/api/minizinc/{userID}/{fileUUID}/', tags=[info.FILES['name']])
def get_file(userID : str, fileUUID : str, req : Request, res : Response):
    header_userID = req.headers.get('userid')
    if header_userID != userID and header_userID != SYS_ID:
        raise HTTPException(status_code=401, detail='Unauthorized')
    if not mysql_storage.file_exists(userID, fileUUID):
        res.status_code = status.HTTP_200_OK
        return "File does not exist"
    return google_storage.generateGetUrl(fileName=fileUUID)


@router.delete('/api/minizinc/{userID}/{fileUUID}', include_in_schema=False)
@router.delete('/api/minizinc/{userID}/{fileUUID}/', tags=[info.FILES['name']])
def delete_file(userID : str, fileUUID : str, req : Request, res : Response):
    header_userID = req.headers.get('userid')
    if header_userID != userID and header_userID != SYS_ID:
        raise HTTPException(status_code=401, detail='Unauthorized')
    if not mysql_storage.file_exists(userID, fileUUID):
        res.status_code = status.HTTP_200_OK
        return "File does not exist"
    files = mysql_storage.get_file(userID, fileUUID)
    google_storage.delete_file(fileUUID)
    row_count = mysql_storage.delete_file(userID, fileUUID)
    return 'Success! - {row_count} file(s) deleted'


app.include_router(router)
