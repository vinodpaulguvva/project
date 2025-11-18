
from pydantic import BaseModel, Field
from typing import List, Optional

class Comment(BaseModel):
    file: str
    line_start: int
    line_end: int
    category: str
    severity: str
    message: str
    suggested_fix: Optional[str]
    confidence: float = Field(..., ge=0.0, le=1.0)

class ReviewResult(BaseModel):
    job_id: str
    summary: str
    comments: List[Comment]
    metrics: dict
