from fastapi import APIRouter

router = APIRouter()

@router.get("")
def read_root():
    return {
        "status": "online",
        "message": "노드 기반 창작 시스템 서버가 정상 작동 중입니다!",
        "version": "0.1.0"
    }