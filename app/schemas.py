from socketserver import ThreadingUnixStreamServer
from telnetlib import theNULL
import uuid
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

class ArtifactResponse(BaseModel):
    public_id: uuid.UUID
    url: str
    content_type: str
    

class PostResponse(BaseModel):
    public_id: uuid.UUID
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    artifacts: Optional[List[ArtifactResponse]] = []
    
    class Config:
        orm_mode = True
        
class ArtifactCreate(BaseModel):
    file_id: str
    file_path: str
    file_type: str
    thumbnail_url: str
    
class PostCreate(BaseModel):
    title: str
    content: str
    artifacts: Optional[List[ArtifactCreate]] = None  # optional