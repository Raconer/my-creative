#!/bin/bash
echo "🔄 [My-Creative] 백엔드 교체 중..."

# 1. 이 프로젝트의 backend 컨테이너만 멈추고 삭제 (다른 도커는 영향 없음)
docker-compose stop backend
docker-compose rm -f backend

# 2. 다시 실행
docker-compose up -d backend

echo "✅ 백엔드가 다시 시작되었습니다. (다른 프로젝트 컨테이너는 안전합니다!)"