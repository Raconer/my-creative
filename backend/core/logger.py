import logging

# 로깅 형식 설정 (시간 - 이름 - 레벨 - 메시지)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("my-creative") # 로거 이름 설정