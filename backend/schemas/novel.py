from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List

# ---------------------------------------------------------
# 📖 공통 필드 정의
# ---------------------------------------------------------
class NovelBase(BaseModel):
    title: str = Field(..., description="소설 프로젝트 제목")
    genre: Optional[str] = Field(None, description="소설 장르 (예: 판타지, 추리)")
    story_summary: Optional[str] = Field(None, description="전체 줄거리 요약")

# ---------------------------------------------------------
# 📥 생성 요청 시 사용 (POST /novels)
# ---------------------------------------------------------
class NovelCreate(NovelBase):
    initial_world: Dict[str, Any] = Field(default={}, description="초기 세계관 설정 (JSON)")
    initial_rules: Dict[str, Any] = Field(default={}, description="집필 규칙 (JSON)")
    description: Optional[str] = Field(None, description="프로젝트 상세 설명")

# ---------------------------------------------------------
# 📤 API 응답 시 사용 (GET /novels/{id})
# ---------------------------------------------------------
class NovelResponse(NovelBase):
    id: int
    world_setting: Dict[str, Any]
    rules: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

# ---------------------------------------------------------
# 🔍 검색 결과용 (필요 시 더 가볍게 구성)
# ---------------------------------------------------------
class NovelSearchResponse(NovelBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
        
        
class GenerateConfig(BaseModel):
    max_attempts: int = Field(10, ge=1, le=20, description="최대 재작성 시도 횟수 (1~20)")
    min_score: int = Field(95, ge=0, le=100, description="통과 최소 점수 (0~100)")