from pydantic import BaseModel

class File(BaseModel):
    userID: str
    fileName: str
    fileUUID: str

class SignedUrl(BaseModel):
    fileUUID: str
    url: str