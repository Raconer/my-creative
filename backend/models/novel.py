from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Novel(Base):
    __tablename__ = "novels"

    id = Column(Integer, primary_key=True, index=True)
    
    # 📖 소설 기본 정보
    title = Column(String(255), nullable=False)
    genre = Column(String(100))
    
    # 🌍 세계관 설정 및 규칙 (JSON)
    world_setting = Column(JSON, default={})
    rules = Column(JSON, default={})
    
    # 📝 전체 줄거리 요약 (매 화가 끝날 때마다 AI가 업데이트)
    story_summary = Column(Text, nullable=True)
    
    # ⏰ 생성 일시
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ---------------------------------------------------------
    # 🔗 관계 설정 (Relationship)
    # ---------------------------------------------------------

    # 📜 집필된 원고들 (1:N)
    chapters = relationship("Chapter", back_populates="novel", cascade="all, delete-orphan")
    
    # ⚙️ 이 소설 전용 AI 프롬프트 설정 (1:1)
    prompts = relationship("PromptSetting", back_populates="novel", uselist=False, cascade="all, delete-orphan")
    
    # 📊 생성 과정 로그 (1:N)
    generation_logs = relationship("GenerationLog", back_populates="novel", cascade="all, delete-orphan")

    # 💡 지식 베이스 에피소드들 (1:N)
    episodes = relationship("Episode", back_populates="novel", cascade="all, delete-orphan")

    # 🎨 캔버스 위 설정 노드들 (1:N)
    nodes = relationship("Node", back_populates="novel", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Novel(id={self.id}, title='{self.title}', genre='{self.genre}')>"