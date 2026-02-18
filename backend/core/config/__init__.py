from .db import DatabaseSettings
from .app import AppSettings

class Settings:
    def __init__(self):
        self.db = DatabaseSettings()
        self.app = AppSettings()
        
    # 이렇게 직접 꺼내주면 settings.APP_NAME으로 접근 가능합니다.
    @property
    def APP_NAME(self):
        return self.app.APP_NAME

settings = Settings()