#!/bin/bash
echo "🔄 [My-Creative] 전체 서비스 재기동 중..."

# 현재 compose 파일에 정의된 서비스만 중지하고 삭제
docker-compose stop
docker-compose rm -f

# 다시 빌드 및 실행
docker-compose up -d --build

echo "✅ 전체 서비스 재시작 완료!"