from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class GenerationLog(Base):
    __tablename__ = "generation_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # 🔗 연결된 소설 정보
    novel_id = Column(Integer, ForeignKey("novels.id", ondelete="CASCADE"), nullable=False)
    
    # 🔢 회차 및 시도 횟수
    chapter_num = Column(Integer, nullable=False)
    attempt_num = Column(Integer, nullable=False)
    
    # ✍️ AI가 생성한 원고 본문
    content = Column(Text, nullable=True)
    
    # 🎯 AI가 스스로 매긴 점수 (0~100)
    score = Column(Integer, default=0)
    
    # 💡 AI 편집자의 비평 및 피드백
    feedback = Column(Text, nullable=True)
    
    # 📦 상세 채점표 (JSON) - 가독성, 사이다, 플롯 등 항목별 점수
    raw_review = Column(JSON, nullable=True)
    
    # ✅ 최종 원고로 채택 여부 (0: 탈락, 1: 채택)
    is_selected = Column(Integer, default=0)
    
    # ⏰ 기록 생성 시각
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 🔗 관계 설정: Novel 모델과의 연결
    novel = relationship("Novel", back_populates="generation_logs")

    def __repr__(self):
        return f"<GenerationLog(novel_id={self.novel_id}, ch={self.chapter_num}, attempt={self.attempt_num}, score={self.score})>"