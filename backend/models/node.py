from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Node(Base):
    __tablename__ = "nodes"

    # 1. ID (Primary Key)
    id = Column(Integer, primary_key=True, index=True)

    # 2. 🔗 연결된 소설 정보 (어느 프로젝트의 캔버스 노드인지)
    novel_id = Column(Integer, ForeignKey("novels.id", ondelete="CASCADE"), nullable=False)

    # 3. 노드 제목 (노드 상단에 표시될 텍스트)
    title = Column(String(255), nullable=False)

    # 4. 노드 상세 내용 (카드 클릭 시 보여줄 세부 설정)
    content = Column(Text, nullable=True)

    # 5. 📍 캔버스 위 위치 (x, y 좌표)
    # 프론트엔드(React-Flow 등)의 드래그 앤 드롭 상태를 저장합니다.
    x_pos = Column(Float, default=0.0)
    y_pos = Column(Float, default=0.0)

    # 6. 생성일 및 수정일
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 🔗 관계 설정: Novel 모델과의 연결
    novel = relationship("Novel", back_populates="nodes")

    def __repr__(self):
        return f"<Node(id={self.id}, title='{self.title}', pos=({self.x_pos}, {self.y_pos}))>"