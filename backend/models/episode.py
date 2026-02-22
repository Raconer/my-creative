from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, index=True)
    
    # 🔗 어느 소설 프로젝트의 에피소드인지 연결
    novel_id = Column(Integer, ForeignKey("novels.id", ondelete="CASCADE"), nullable=False)
    
    # 🔢 에피소드 순서 (예: world.json의 episode_number)
    episode_number = Column(Integer, nullable=False)
    
    # 🏷️ 에피소드 제목 (예: "커피, 악마의 음료인가 신의 선물인가")
    title = Column(String(255), nullable=False)
    
    # 📝 에피소드 전체 요약
    summary = Column(Text, nullable=True)
    
    # 📦 세부 스토리 리스트, 거짓말 개수, 정답(Solution) 등을 통째로 저장
    # world.json의 'stories', 'solution', 'entities' 등을 담기에 최적입니다.
    detail_data = Column(JSON, nullable=False)

    # ⏰ 데이터 생성/수정 시간 (관리용)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 🔗 관계 설정
    novel = relationship("Novel", back_populates="episodes")

    def __repr__(self):
        return f"<Episode(novel_id={self.novel_id}, num={self.episode_number}, title='{self.title}')>"