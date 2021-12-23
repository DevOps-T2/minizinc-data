from fastapi import FastAPI, Query, HTTPException, APIRouter, Request, Response, status
from typing import Optional
from typing import List

import google_storage
import mysql_storage
import info
import models


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
    """
    Returns a *fileUUID* and a signed url.  
    The signed url can be used to **PUT** a file into storage.  \n
    After a file has been uploaded a call to */api/minizinc/upload* with the returned  
    *fileUUID* should be made in order to commit that the file has been stored.  \n
    If a *userID* and *fileUUID* is given, it will instead give you a link to  
    an already existing file where any **PUT** requests to the link will overwrite  
    the file that is already there.  
    """
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
    """
    This endpoint is meant to be used after a file has been uploaded to a signed url,  
    this endpoint essentially stores and keeps track of which files belongs to which user,  
    therefore after a file as been uploaded to a signed url it must be commited here afterwards.  
    """
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
    """
    Returns a list of all the files the user has.
    """
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
    """
    Deletes the user and all of its files.
    """
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
    """
    Returns a signed url to the file with the given *fileUUID*.  
    A signed url is a link that can be used to download the file.  
    Anyone who has access to the link also has access to the file.  
    The link **expires** 15 minutes after creation.  
    """
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
    """
    Deletes a file for a user
    """
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
