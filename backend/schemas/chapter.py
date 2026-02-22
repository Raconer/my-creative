from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# ---------------------------------------------------------
# 📖 공통 필드 정의 (상속용)
# ---------------------------------------------------------
class ChapterBase(BaseModel):
    chapter_num: int = Field(..., description="회차 번호 (1, 2, 3...)")
    content: str = Field(..., description="집필된 소설 본문")

# ---------------------------------------------------------
# 📥 생성/수정 요청 시 사용 (필요 시 확장 가능)
# ---------------------------------------------------------
class ChapterCreate(ChapterBase):
    novel_id: int
    score: int = 0
    feedback: Optional[str] = None

# ---------------------------------------------------------
# 📤 API 응답 시 사용 (최종 결과물 데이터 규격)
# ---------------------------------------------------------
class ChapterResponse(ChapterBase):
    id: int
    novel_id: int
    score: int = Field(..., description="AI가 매긴 최종 원고 점수")
    feedback: Optional[str] = Field(None, description="AI 편집자의 한 줄 비평")
    created_at: datetime

    class Config:
        # SQLAlchemy 모델 객체를 Pydantic 모델로 자동 변환 (ORM 모드)
        from_attributes = True