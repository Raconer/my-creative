from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class DatabaseSettings(BaseSettings):
    # 1. DB 접속 정보 (기본값 설정)
    DB_HOST: str = Field(default="127.0.0.1")
    DB_PORT: int = Field(default=3306)
    DB_USER: str = Field(default="root")
    DB_PASSWORD: str = Field(default="root")
    DB_NAME: str = Field(default="creative")

    # 2. 실행 전략 (환경에 따라 update 또는 none)
    DB_STRATEGY: str = Field(default="none")

    # 3. SQLAlchemy에서 사용할 URL 생성 프로퍼티
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # 4. .env 파일 설정
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # .env에 정의되지 않은 변수가 있어도 무시
    )