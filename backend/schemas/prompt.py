from pydantic import BaseModel, Field
from typing import Optional

# ---------------------------------------------------------
# 📖 공통 필드 정의 (프롬프트의 핵심 내용)
# ---------------------------------------------------------
class PromptBase(BaseModel):
    plot_prompt: str = Field(..., description="1단계: 플롯 생성용 템플릿 ({chapter_num}, {lie_count} 등 포함)")
    writing_prompt: str = Field(..., description="2단계: 본문 작성용 템플릿 ({plot}, {world}, {context} 등 포함)")
    review_prompt: str = Field(..., description="3단계: 비평/평가용 템플릿 (JSON 형식 응답 강제)")
    summary_prompt: str = Field(..., description="4단계: 요약/갱신용 템플릿 ({content}, {old_summary} 포함)")

# ---------------------------------------------------------
# 📥 프롬프트 수정 요청 시 사용 (특정 필드만 수정 가능하도록 Optional 설정)
# ---------------------------------------------------------
class PromptUpdate(BaseModel):
    plot_prompt: Optional[str] = None
    writing_prompt: Optional[str] = None
    review_prompt: Optional[str] = None
    summary_prompt: Optional[str] = None

# ---------------------------------------------------------
# 📤 API 응답 시 사용
# ---------------------------------------------------------
class PromptResponse(PromptBase):
    id: int
    novel_id: int

    class Config:
        from_attributes = True