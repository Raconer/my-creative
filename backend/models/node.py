from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from sqlalchemy.sql import func
from database import Base

class Node(Base):
    __tablename__ = "nodes"  # 실제 MySQL에 생성될 테이블 이름

    # 1. ID (Primary Key)
    id = Column(Integer, primary_key=True, index=True)

    # 2. 노드 제목 (Varchar 255)
    title = Column(String(255), nullable=False)

    # 3. 노드 내용 (Long Text)
    content = Column(Text, nullable=True)

    # 4. 캔버스 위 위치 (x, y 좌표)
    # 나중에 프론트에서 드래그 앤 드롭으로 배치할 때 필요합니다.
    x_pos = Column(Float, default=0.0)
    y_pos = Column(Float, default=0.0)

    # 5. 생성일 및 수정일 (Spring의 @CreatedDate, @LastModifiedDate 느낌)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())