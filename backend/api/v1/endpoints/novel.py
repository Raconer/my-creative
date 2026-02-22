from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from database import get_db, SessionLocal
from schemas.novel import GenerateConfig, NovelCreate, NovelResponse
from modules.generator import NovelGenerator
from service.novel_service import NovelService

router = APIRouter()

# ----------------------------------------------------------------
# 🚀 백그라운드 전용 독립 실행 함수
# ----------------------------------------------------------------
def run_generator_task(novel_id: int, config_dict: Dict[str, Any]):
    """백그라운드에서 실행될 실제 로직"""
    db = SessionLocal()
    try:
        generator = NovelGenerator(db, novel_id)
        generator.run_daily_routine(config_dict)
    finally:
        db.close()

# ----------------------------------------------------------------
# 🔍 소설 검색 API
# ----------------------------------------------------------------
@router.get("/search", summary="🔍 통합 콘텐츠 검색")
def search_novel(
    keyword: str | None = Query(None, description="제목, 줄거리, 세계관 키워드 검색"),
    novelService: NovelService = Depends()
):
    return novelService.search_content(keyword)

# ----------------------------------------------------------------
# 📝 소설 프로젝트 생성 API
# ----------------------------------------------------------------
@router.post("/", response_model=NovelResponse, summary="📝 새로운 소설 프로젝트 생성")
def create_novel_project(
    novel_in: NovelCreate, 
    novelService: NovelService = Depends()
):
    return novelService.create_novel(novel_in)

# ----------------------------------------------------------------
# ✨ AI 소설 집필 API (비동기 처리 최적화)
# ----------------------------------------------------------------
@router.post("/{novel_id}/generate", summary="✨ AI 소설 자동 집필 시작")
def generate_novel_chapter(
    novel_id: int, 
    config: GenerateConfig, 
    background_tasks: BackgroundTasks,
    novelService: NovelService = Depends()
):
    novel = novelService.get_novel(novel_id)
    if not novel:
        raise HTTPException(status_code=404, detail="소설 없음")

    # ✅ 함수 이름(run_generator_task)만 넘기고, 인자는 쉼표로 나열합니다.
    # config.dict()는 Pydantic v1 기준이며, v2라면 config.model_dump()를 권장합니다.
    config_data = config.model_dump() if hasattr(config, 'dict') else config.model_dump()
    
    background_tasks.add_task(run_generator_task, novel_id, config_data)

    return {
        "status": "started",
        "message": f"최대 {config.max_attempts}회, 목표 {config.min_score}점으로 집필을 시작합니다."
    }
# ----------------------------------------------------------------
# 📊 히스토리 조회 API
# ----------------------------------------------------------------
@router.get("/{novel_id}/history", summary="📊 생성 프로세스 히스토리 조회")
def get_novel_history(novel_id: int, novelService: NovelService = Depends()):
    return novelService.get_history(novel_id)