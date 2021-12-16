from pydantic import BaseModel

class File(BaseModel):
    userID: int
    fileName: str
    fileUUID: str

class SignedUrl(BaseModel):
    fileUUID: str
    url: str