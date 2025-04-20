from pydantic import BaseModel
from uuid import UUID

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserGet(BaseModel):
    id: str
    username: str
    email: str

class GraphCreate(BaseModel):
    user_id: str
    name: str

class GraphResponse(BaseModel):
    id: str
    user_id: str
    name: str