from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings

def setup_middleware(app: FastAPI) -> None:
    """
    CORS 및 기타 미들웨어 설정을 담당하는 함수
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.app.ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 나중에 로그 기록, 인증 체크 미들웨어 등을 여기에 추가하면 관리하기 편합니다.