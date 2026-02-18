#!/bin/bash

# 1. backend 폴더로 이동
cd backend

# 2. 가상환경(.venv)이 있는지 확인하고, 없으면 생성
if [ ! -d ".venv" ]; then
    echo "🌐 가상환경이 없어서 새로 생성합니다..."
    python3 -m venv .venv
fi

# 3. 가상환경 활성화
source .venv/bin/activate

# 4. 필수 라이브러리 설치/업데이트 (requirements.txt 기준)
echo "📦 라이브러리 상태를 체크합니다..."
pip install --upgrade pip
pip install -r requirements.txt

# 5. FastAPI 서버 실행 (Hot Reload 모드)
echo "🚀 로컬 서버를 실행합니다! (http://127.0.0.1:8000)"
uvicorn main:app --reload --host 0.0.0.0 --port 8000