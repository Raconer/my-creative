from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings
from core.logger import logger

# 1. SQLAlchemy 엔진 생성 (연결 통로)
engine = create_engine(settings.db.DATABASE_URL)

# 2. 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. 모델의 부모 클래스
Base = declarative_base()

def check_db_connection():
    """단순 연결 확인용 함수 (SELECT 1 쿼리 실행)"""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"❌ DB 연결 상태 확인 실패: {e}")
        return False

def init_db():
    """서버 시작 시 호출할 DB 초기화 함수"""
    
    # 🚀 [핵심] 여기서 모든 모델을 다 불러와야 KeyError가 안 터집니다!
    import models

    # 1. DB_STRATEGY가 'update'인 경우 테이블 자동 생성
    if settings.db.DB_STRATEGY == "update":
        logger.info("🛠️ DB_STRATEGY='update': 테이블 동기화를 시작합니다.")
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("📊 모든 데이터베이스 테이블 동기화 완료")
        except Exception as e:
            logger.error(f"❌ 테이블 생성 중 오류 발생: {e}")
            raise e
    else:
        logger.info(f"⏭️ DB_STRATEGY='{settings.db.DB_STRATEGY}': 테이블 생성을 건너뜁니다.")

    # 2. 최종 연결 확인 및 로그 출력
    if check_db_connection():
        logger.info("✨ 데이터베이스 연결 및 준비가 완료되었습니다.")
    else:
        logger.warning("⚠️ 데이터베이스 연결에 문제가 있습니다. 설정을 확인하세요.")

def get_db():
    """FastAPI의 Dependency Injection용 함수"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()