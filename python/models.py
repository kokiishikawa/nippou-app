from pydantic import BaseModel
from typing import Optional

class NippouCreate(BaseModel):
    date: str
    timeblock: str
    theme: str
    details: str
    tomorrow: str
    note: Optional[str] = None

class NippouResponse(BaseModel):
    date: str
    timeblock: str
    theme: str
    details: str
    tomorrow: str
    note: Optional[str] = None
    created_at: str
    updated_at: str