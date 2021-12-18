from google.cloud import storage
from google.oauth2 import service_account
from google import auth
from datetime import timedelta
from models import SignedUrl
import uuid


CREDENTIALS = service_account.Credentials.from_service_account_file('key.json')
#STORAGE_CLIENT = storage.Client(credentials=CREDENTIALS)
BUCKET_NAME = 'minizinc_data'

# Any link generated will expire in x mintues from now where x=EXPIRE_MINUTES
EXPIRE_MINUTES = 15


def generatePostUrl(fileName=None):
    bucket = STORAGE_CLIENT.bucket(BUCKET_NAME)
    if fileName is None:
        fileName = str(uuid.uuid4())
    file = bucket.blob(fileName)
    
    expires = expire_timestamp(EXPIRE_MINUTES)
    return SignedUrl(
        fileUUID=fileName, 
        url=file.generate_signed_url(
            version='v4',
            expiration=expires,
            method='PUT'
    ))


def generateGetUrl(fileName):
    bucket = STORAGE_CLIENT.bucket(BUCKET_NAME)
    file = bucket.blob(fileName)

    expires = expire_timestamp(EXPIRE_MINUTES)
    return file.generate_signed_url(
        version='v4',
        expiration=expires,
        method='GET'
    )


def file_exists(fileName):
    bucket = STORAGE_CLIENT.bucket(BUCKET_NAME)
    file = bucket.blob(fileName)
    return file.exists()


def delete_file(fileName):
    bucket = STORAGE_CLIENT.bucket(BUCKET_NAME)
    file = bucket.blob(fileName)
    file.delete()


def expire_timestamp(minutes):
    return timedelta(minutes=minutes)

