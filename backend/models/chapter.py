from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    novel_id = Column(Integer, ForeignKey("novels.id", ondelete="CASCADE"), nullable=False)
    
    # 📖 회차 번호 (1화, 2화...)
    chapter_num = Column(Integer, nullable=False)
    
    # ✍️ 집필된 소설 본문
    content = Column(Text, nullable=False)
    
    # 🎯 AI가 매긴 최종 원고 점수 (0~100)
    score = Column(Integer, default=0)
    
    # 💡 해당 원고에 대한 AI의 최종 피드백
    feedback = Column(Text, nullable=True)
    
    # ⏰ 생성 일시
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 🔗 관계 설정: Novel 모델과의 연결
    novel = relationship("Novel", back_populates="chapters")

    def __repr__(self):
        return f"<Chapter(novel_id={self.novel_id}, num={self.chapter_num}, score={self.score})>"