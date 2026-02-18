from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Novel(Base):
    __tablename__ = "novels"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    genre = Column(String(100), default="Fantasy")
    
    world_setting = Column(JSON, default={}) 
    rules = Column(JSON, default={})         
    story_summary = Column(Text, nullable=True) 

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    chapters = relationship("Chapter", back_populates="novel", cascade="all, delete-orphan")

class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    novel_id = Column(Integer, ForeignKey("novels.id"), nullable=False)
    
    chapter_num = Column(Integer, nullable=False) 
    title = Column(String(255), default="무제")   
    content = Column(Text, nullable=False)        
    
    score = Column(Integer, default=0)
    feedback = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    novel = relationship("Novel", back_populates="chapters")