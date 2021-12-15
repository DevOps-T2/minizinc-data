from pydantic import BaseModel

class File(BaseModel):
    userID: int
    fileName: str
    fileUUID: str