from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings
from core.logger import logger

# 1. SQLAlchemy 엔진 생성 (연결 통로)
# settings.db.DATABASE_URL을 통해 .env에 설정된 MySQL 주소를 가져옵니다.
engine = create_engine(settings.db.DATABASE_URL)

# 2. 세션 팩토리 생성 (Spring의 SessionFactory/EntityManager 느낌)
# 실제 DB 작업 시 이 SessionLocal을 호출해서 사용합니다.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. 모델의 부모 클래스 (JPA의 @Entity들이 상속받을 대상)
Base = declarative_base()

def check_db_connection():
    """
    단순 연결 확인용 함수 (SELECT 1 쿼리 실행)
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"❌ DB 연결 상태 확인 실패: {e}")
        return False

def init_db():
    """
    서버 시작 시 호출할 DB 초기화 함수.
    .env의 DB_STRATEGY 설정에 따라 테이블을 생성하거나 연결만 확인합니다.
    """
    # [중요] 테이블 생성을 위해 모델 파일들을 여기서 import 해야 합니다.
    import models.node 

    # 1. DB_STRATEGY가 'update'인 경우 테이블 자동 생성
    if settings.db.DB_STRATEGY == "update":
        logger.info(f"🛠️ DB_STRATEGY='update': 테이블 동기화를 시작합니다.")
        try:
            # Base에 등록된 모든 테이블 정보를 바탕으로 MySQL에 테이블 생성
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
    """
    FastAPI의 Dependency Injection용 함수.
    API 호출마다 세션을 생성하고 작업이 끝나면 자동으로 닫아줍니다.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()