from typing import List
from pydantic import BaseModel

class UserInput(BaseModel):
    content: str
    type: str
    duration: str
    projectId: str


class VideoData(BaseModel):
    imageUrl: str
    script: str


class VideoInput(BaseModel):
    data: List[VideoData]
    projectId: str
    email: str
