from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.novel import NovelCreate, NovelResponse, ChapterResponse
from modules.novel_manager import NovelManager
from modules.generator import NovelGenerator

router = APIRouter()

# 1. 새로운 소설 프로젝트 생성 API
@router.post("/", response_model=NovelResponse)
def create_novel_project(novel_in: NovelCreate, db: Session = Depends(get_db)):
    manager = NovelManager(db)
    return manager.create_novel(novel_in)

# 2. 🌟 소설 1화 자동 작성 실행 API 
@router.post("/{novel_id}/generate", response_model=ChapterResponse)
def generate_novel_chapter(novel_id: int, db: Session = Depends(get_db)):
    manager = NovelManager(db)
    novel = manager.get_novel(novel_id)
    if not novel:
        raise HTTPException(status_code=404, detail="소설을 찾을 수 없습니다.")
    
    generator = NovelGenerator(manager, novel_id)
    chapter = generator.run_daily_routine()
    
    if not chapter:
        raise HTTPException(status_code=500, detail="챕터 생성에 실패했습니다.")
    
    return chapter