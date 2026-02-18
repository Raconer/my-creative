from sqlalchemy.orm import Session
from models.novel import Novel, Chapter
from schemas.novel import NovelCreate

class NovelManager:
  def __init__(self, db: Session):
      self.db = db

  def create_novel(self, novel_in: NovelCreate):
    db_novel = Novel(
        title=novel_in.title,
        genre=novel_in.genre,
        world_setting=novel_in.initial_world if novel_in.initial_world else {},
        rules=novel_in.initial_rules if novel_in.initial_rules else {},
        story_summary=novel_in.description
    )
    self.db.add(db_novel)
    self.db.commit()
    self.db.refresh(db_novel)
    return db_novel

  def get_novel(self, novel_id: int):
    return self.db.query(Novel).filter(Novel.id == novel_id).first()

  def get_last_chapter_num(self, novel_id: int) -> int:
    last_chapter = self.db.query(Chapter).filter(Chapter.novel_id == novel_id).order_by(Chapter.chapter_num.desc()).first()
    # int()로 감싸서 VS Code에게 숫자임을 확실히 알려줍니다!
    return int(last_chapter.chapter_num) if last_chapter else 0 # type: ignore

  def get_recent_context(self, novel_id: int, count: int = 5) -> str:
    chapters = self.db.query(Chapter).filter(Chapter.novel_id == novel_id).order_by(Chapter.chapter_num.desc()).limit(count).all()
    chapters.reverse() 
    combined_text = "".join([f"\n[Chapter {c.chapter_num}]\n{c.content}\n" for c in chapters])
    return combined_text

  def save_chapter(self, novel_id: int, chapter_num: int, content: str, score: int, feedback: str = ""):
    db_chapter = Chapter(
        novel_id=novel_id,
        chapter_num=chapter_num,
        title=f"제 {chapter_num}화",
        content=content,
        score=score,
        feedback=feedback
    )
    self.db.add(db_chapter)
    self.db.commit()
    self.db.refresh(db_chapter)
    return db_chapter

  def update_world_and_summary(self, novel_id: int, new_world: dict, new_summary: str):
    novel = self.get_novel(novel_id)
    if novel:
        novel.world_setting = new_world    # type: ignore
        novel.story_summary = new_summary  # type: ignore
        self.db.commit()
        self.db.refresh(novel)
    return novel