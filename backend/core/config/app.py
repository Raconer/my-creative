from pydantic_settings import BaseSettings
from typing import List

class AppSettings(BaseSettings):
    ENV: str = "development"
    APP_NAME: str = "CreativeNodeServer"
    ALLOW_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        extra = "ignore"