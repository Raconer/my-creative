from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from database import SessionLocal
from schemas.novel import GenerateConfig, NovelCreate, NovelResponse
from modules.generator import NovelGenerator
from service.novel_service import NovelService

router = APIRouter()

# ----------------------------------------------------------------
# 🔒 중복 실행 방지를 위한 전역 메모리 셋(Set)
# ----------------------------------------------------------------
active_generations = set()

# ----------------------------------------------------------------
# 🚀 백그라운드 태스크 (독립 세션 관리)
# ----------------------------------------------------------------
def run_generator_task(novel_id: int, config_dict: Dict[str, Any]):
    db = SessionLocal()
    try:
        generator = NovelGenerator(db, novel_id)
        generator.run_daily_routine(config_dict)
    finally:
        # DB 세션을 닫으면서, 진행 중 목록에서도 반드시 삭제 (에러가 나더라도 무조건 실행됨)
        db.close()
        active_generations.discard(novel_id)

# ----------------------------------------------------------------
# 🔍 소설 검색 API
# ----------------------------------------------------------------
@router.get("/search", summary="🔍 통합 콘텐츠 검색")
def search_novel(
    keyword: str | None = Query(None, description="제목, 줄거리, 세계관 키워드 검색"),
    novel_service: NovelService = Depends()
):
    return novel_service.search_content(keyword)

# ----------------------------------------------------------------
# 📝 소설 프로젝트 생성 API
# ----------------------------------------------------------------
@router.post("/", response_model=NovelResponse, summary="📝 새로운 소설 프로젝트 생성")
def create_novel_project(
    novel_in: NovelCreate, 
    novel_service: NovelService = Depends()
):
    return novel_service.create_novel(novel_in)

# ----------------------------------------------------------------
# ✨ AI 소설 집필 API (비동기 처리 & 중복 방지)
# ----------------------------------------------------------------
@router.post("/{novel_id}/generate", summary="✨ AI 소설 자동 집필 시작")
def generate_novel_chapter(
    novel_id: int, 
    config: GenerateConfig, 
    background_tasks: BackgroundTasks,
    novel_service: NovelService = Depends()
):
    # 🚨 1. 중복 실행 검증 (가장 먼저 체크하여 DB 조회 비용 아끼기)
    if novel_id in active_generations:
        raise HTTPException(
            status_code=429, # 429 Too Many Requests
            detail="⚠️ 현재 이 소설은 이미 AI가 집필을 진행 중입니다. 완료될 때까지 잠시만 기다려주세요."
        )

    # 2. 소설 존재 여부 사전 검증
    if not novel_service.get_novel(novel_id):
        raise HTTPException(status_code=404, detail="해당 소설을 찾을 수 없습니다.")

    # 3. Pydantic v2 객체를 딕셔너리로 변환
    config_data = config.model_dump()
    
    # 🔒 4. 락(Lock) 걸기: 진행 중 목록에 소설 ID 추가
    active_generations.add(novel_id)
    
    # 5. 백그라운드 작업 큐에 등록
    background_tasks.add_task(run_generator_task, novel_id, config_data)

    return {
        "status": "started",
        "message": f"최대 {config.max_attempts}회, 목표 {config.min_score}점으로 집필을 시작합니다."
    }

# ----------------------------------------------------------------
# 📊 히스토리 조회 API
# ----------------------------------------------------------------
@router.get("/{novel_id}/history", summary="📊 생성 프로세스 히스토리 조회")
def get_novel_history(
    novel_id: int, 
    novel_service: NovelService = Depends()
):
    return novel_service.get_history(novel_id)