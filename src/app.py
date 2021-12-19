from http.client import responses
from os import stat
from fastapi import FastAPI, Query, HTTPException, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import google_storage
import mysql_storage
import info
import models
import json

UPLOAD_URL = '/api/minizinc/upload'

app = FastAPI(
    title=info.TITLE,
    version=info.VERSION,
    description=info.DESCRIPTION,
    openapi_tags=info.TAGS_METADATA
)
router = APIRouter()

def is_upload_endpoint(endpoint):
    return endpoint == UPLOAD_URL or endpoint == f'{UPLOAD_URL}/'


async def extract_user_id(request):
    if (request.method == 'POST'):
        # User id is in body
        print("BODY")
        body = await request.body()
        body = body.decode()
        body = json.loads(body)
        request_userID = body['userID']
    elif('userID' in request.query_params):
        # User id is in query param (they are not gauranteed to be here)
        print("QUERY PARAMS")
        request_userID = request.query_params['userID']
    else:
        # Hack to obtain the userID when its in the path, might break the middleware if a new endpoint is created.
        print("PATH PARAMS")
        request_userID = request.url.path.split('/')[3]
    return request_userID


@app.middleware('http')
async def authorize(request: Request, call_next):
    if request.url.path == '/openapi.json' or request.url.path == '/docs':
        response = await call_next(request)
        return response
    # edge case for requesting an upload url.
    if is_upload_endpoint(request.url.path) and 'userID' not in request.query_params and request.method == 'GET':
        response = await call_next(request)
        return response
    
    header_userID = request.headers.get('userid').strip()
    request_userID = (await extract_user_id(request)).strip()

    if request_userID != header_userID and request.headers.get('role') != 'admin':
        return JSONResponse(status_code=401)
    if request_userID != header_userID and request.headers.get('role') == 'admin' and request.method != 'DELETE':
        # Admins are only allowed to delete users file, not use/manipulate other users files.
        return JSONResponse(status_code=401) 
    print("reuqest")
    response = await call_next(request)
    print("done!")
    return response


# Had to include double route with and without trailing backslash to please the gateway-gods
# See: https://github.com/tiangolo/fastapi/issues/2060
@router.get(UPLOAD_URL, response_model=models.SignedUrl, include_in_schema=False)
@router.get(f'{UPLOAD_URL}/', response_model=models.SignedUrl, tags=[info.UPLOAD['name']])
def get_signed_upload_url(userID : Optional[str] = Query(None), fileUUID: Optional[str] = Query(None)):
    # If UUID is given, it will create a link for PUT where you can update what is already stored
    # If UUID is not given you will be given a link for PUT where you can create a NEW file.
    if fileUUID and userID:
        if not mysql_storage.file_exists(userID, fileUUID):
            raise HTTPException(status_code=404, detail='There does not exist a file with the given identifier')
        return google_storage.generatePostUrl(fileUUID)
    else:
        return google_storage.generatePostUrl()


@router.post('/api/minizinc/upload', include_in_schema=False)
@router.post('/api/minizinc/upload/', tags=[info.UPLOAD['name']])
def upload_file(file: models.File):
    if not google_storage.file_exists(file.fileUUID):
        return HTTPException(status_code=400, detail='No such file found in storage')
    if mysql_storage.file_exists(file.userID, file.fileUUID):
        mysql_storage.update_file(file)
        return "File Updated!"
    mysql_storage.create_file(file)
    return "File uploaded!"


@router.get('/api/minizinc/{userID}', include_in_schema=False)
@router.get('/api/minizinc/{userID}/', tags=[info.FILES['name']])
def get_user_files(userID : str):
    if not mysql_storage.user_exists(userID):
        # No user files found
        return []
    return mysql_storage.get_files(userID)


@router.delete('/api/minizinc/{userID}', include_in_schema=False)
@router.delete('/api/minizinc/{userID}/', tags=[info.FILES['name']])
def delete_user(userID : str):
    files = mysql_storage.get_files(userID)
    for file in files:
        google_storage.delete_file(file.fileUUID)
    # Delete all files for the user from google storage.
    row_count = mysql_storage.delete_files(userID)
    return f'Success! - {row_count} file(s) deleted'


@router.get('/api/minizinc/{userID}/{fileUUID}', include_in_schema=False)
@router.get('/api/minizinc/{userID}/{fileUUID}/', tags=[info.FILES['name']])
def get_file(userID : str, fileUUID : str):
    if not mysql_storage.file_exists(userID, fileUUID):
        raise HTTPException(status_code=404, detail='No such file exists for the given user.')
    return google_storage.generateGetUrl(fileName=fileUUID)


@router.delete('/api/minizinc/{userID}/{fileUUID}', include_in_schema=False)
@router.delete('/api/minizinc/{userID}/{fileUUID}/', tags=[info.FILES['name']])
def delete_file(userID : str, fileUUID : str):
    if not mysql_storage.file_exists(userID, fileUUID):
        raise HTTPException(status_code=404, detail='No such file exists for the given user')
    files = mysql_storage.get_file(userID, fileUUID)
    google_storage.delete_file(fileUUID)
    row_count = mysql_storage.delete_file(userID, fileUUID)
    return 'Success! - {row_count} file(s) deleted'


app.include_router(router)