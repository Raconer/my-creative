echo "🛑 [My-Creative] 서비스 중단 중..."

# 현재 compose 파일에 정의된 컨테이너만 멈춥니다.
# (docker system prune 같은 위험한 명령어는 절대 쓰지 않습니다.)
docker-compose stop

echo "✅ My-Creative 서비스만 종료되었습니다."