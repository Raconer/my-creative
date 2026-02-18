from pydantic import BaseModel, Field
from typing import Dict, Optional, Any
from datetime import datetime

class ChapterBase(BaseModel):
    chapter_num: int
    title: Optional[str] = "무제"
    content: str
    
class ChapterResponse(ChapterBase):
    id: int
    novel_id: int
    score: int
    feedback: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class NovelBase(BaseModel):
    title: str
    genre: str = "Fantasy"

class NovelCreate(NovelBase):
    initial_world: Optional[Dict[str, Any]] = Field(default_factory=dict)
    initial_rules: Optional[Dict[str, Any]] = Field(default_factory=dict)
    description: Optional[str] = "이야기의 시작"

class NovelResponse(NovelBase):
    id: int
    story_summary: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True