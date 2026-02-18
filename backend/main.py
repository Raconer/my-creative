from contextlib import asynccontextmanager
from fastapi import FastAPI

from core.config import settings
from core.logger import logger
from core.middleware import setup_middleware
from database import init_db

from api.v1.api import api_router  # 1. api_router를 import 하세요

@asynccontextmanager
async def lifespan(app: FastAPI):
    # [Startup] DB 초기화 및 테이블 동기화
    logger.info(f"🚀 {settings.app.APP_NAME} 서버 기동 중...")
    try:
        init_db()
    except Exception as e:
        logger.error(f"❌ 초기화 중 치명적 오류 발생: {e}")
    
    yield  # --- 서버 가동 ---
    
    # [Shutdown]
    logger.info("🛑 서버 종료.")

def get_application() -> FastAPI:
    _app = FastAPI(
        title=settings.app.APP_NAME,
        lifespan=lifespan
    )

    # 미들웨어 설정 적용
    setup_middleware(_app)

    # TODO: 라우터 등록 (이곳에 나중에 api_router를 연결할 예정입니다)
    _app.include_router(api_router)

    return _app

app = get_application()