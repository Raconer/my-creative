from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class PromptSetting(Base):
    __tablename__ = "prompt_settings"

    id = Column(Integer, primary_key=True, index=True)
    
    # 🔗 소설 프로젝트와 1:1 연결 (unique=True로 중복 설정 방지)
    novel_id = Column(Integer, ForeignKey("novels.id", ondelete="CASCADE"), unique=True)
    
    # 📝 1단계: 플롯 생성용 프롬프트 (기승전결 설계)
    plot_prompt = Column(Text, nullable=False)
    
    # ✍️ 2단계: 본문 집필용 프롬프트 (모바일 가독성, 캐릭터 페르소나 포함)
    writing_prompt = Column(Text, nullable=False)
    
    # 🧐 3단계: AI 자가 비평 및 채점용 프롬프트 (JSON 형식 강제)
    review_prompt = Column(Text, nullable=False)
    
    # 📑 4단계: 전체 줄거리 요약 및 갱신용 프롬프트
    summary_prompt = Column(Text, nullable=False)

    # 🔗 관계 설정: Novel 모델과의 1:1 연결
    novel = relationship("Novel", back_populates="prompts")

    def __repr__(self):
        return f"<PromptSetting(novel_id={self.novel_id})>"