from google.cloud import storage
from google.oauth2 import service_account
from google import auth
import uuid
from datetime import timedelta

CREDENTIALS = service_account.Credentials.from_service_account_file('key.json')
STORAGE_CLIENT = storage.Client(credentials=CREDENTIALS)
BUCKET_NAME = 'minizinc_data'
EXPIRE_MINUTES = 15


def generatePostUrl(fileName=None):
    bucket = STORAGE_CLIENT.bucket(BUCKET_NAME)
    if fileName is None:
        fileName = str(uuid.uuid4())
    file = bucket.blob(fileName)
    print(file)
    
    # Expires in 15 minutes
    expires = expire_timestamp(EXPIRE_MINUTES)
    return file.generate_signed_url(
        version='v4',
        expiration=expires,
        method='PUT'
    )


def generateGetUrl(fileName):
    bucket = STORAGE_CLIENT.bucket(BUCKET_NAME)
    file = bucket.blob(fileName)

    expires = expire_timestamp(EXPIRE_MINUTES)
    return file.generate_signed_url(
        version='v4',
        expiration=expires,
        method='GET'
    )


def expire_timestamp(minutes):
    return timedelta(minutes=minutes)