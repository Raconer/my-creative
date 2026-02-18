from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# .env 파일 읽어오기
load_dotenv()

app = FastAPI(title=os.getenv("APP_NAME", "CreativeNode"))

# 리액트(Frontend)와 통신을 위한 보안 해제 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용 (로컬 개발용)
    allow_methods=["*"],  # 모든 HTTP 메서드 허용 (GET, POST 등)
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """
    서버가 살아있는지 확인하는 기본 엔드포인트
    """
    return {
        "status": "online",
        "message": "노드 기반 창작 시스템 서버가 정상 작동 중입니다!",
        "version": "0.1.0"
    }

# 실행 명령어 안내용 (터미널에서 직접 실행 시 활용)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)