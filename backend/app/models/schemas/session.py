from pydantic import BaseModel
from typing import Optional


class SessionCreate(BaseModel):
    name: str = ""
    source_type: str  # IMAGE | VIDEO | WEBCAM


class SessionOut(BaseModel):
    id: str
    name: str
    source_type: str
    source_filename: Optional[str]
    status: str
    created_at: int
    closed_at: Optional[int]
    total_frames: int
    final_state: Optional[str]

    model_config = {"from_attributes": True}
