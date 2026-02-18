import json
from core.logger import logger
from modules.ai_driver import AIDriver
from modules.novel_manager import NovelManager

class NovelGenerator:
  def __init__(self, manager: NovelManager, novel_id: int):
    self.manager = manager
    self.novel_id = novel_id
    self.ai = AIDriver()

  def run_daily_routine(self):
    novel = self.manager.get_novel(self.novel_id)
    
    if not novel:
      raise ValueError(f"❌ 소설 ID {self.novel_id}를 찾을 수 없습니다.")
    
      
    world = novel.world_setting
    rules = novel.rules
    summary = novel.story_summary or "이야기의 시작"
    
    current_chapter_num = self.manager.get_last_chapter_num(self.novel_id) + 1
    recent_context = self.manager.get_recent_context(self.novel_id, count=10)

    logger.info(f"💡 [Novel {self.novel_id}] {current_chapter_num}화 플롯 구상 중...")
    plot_prompt = f"다음 소설의 {current_chapter_num}화 플롯을 작성해. 세계관: {world}, 지금까지 줄거리: {summary}"
    plot_plan = self.ai.generate(plot_prompt)

    best_score = 0
    best_content = ""
    current_feedback = "없음"

    for attempt in range(1, 11):
        logger.info(f"🔄 시도 {attempt}/10 (이전 피드백: {current_feedback})")
        
        write_prompt = f"플롯: {plot_plan}\n규칙: {rules}\n이전내용: {recent_context}\n피드백: {current_feedback}\n이 정보를 바탕으로 {current_chapter_num}화 본문을 써줘. 최소 500자 이상."
        content = self.ai.generate(write_prompt)
        
        if not content or len(content) < 500:
            continue

        review_prompt = f"본문: {content}\n이 본문을 평가해서 JSON 형식으로 {{'score': 0~100, 'feedback': '...'}} 반환해."
        review_json = self.ai.generate_json(review_prompt)
        
        try:
            review_data = json.loads(review_json)
            score = int(review_data.get("score", 0))
            current_feedback = review_data.get("feedback", "피드백 없음")

            if score > best_score:
                best_score = score
                best_content = content

            if score >= 90:
                logger.info(f"✅ 통과! ({score}점)")
                break
        except Exception:
            continue
    
    # 1. 챕터 저장
    chapter = self.manager.save_chapter(self.novel_id, current_chapter_num, best_content, best_score, current_feedback)
    
    # 2. 세계관/요약 갱신
    logger.info("🌍 세계관 및 요약 갱신 중...")
    new_world = self._update_world(best_content, world)
    
    summary_prompt = f"기존 줄거리: {summary}\n새 내용: {best_content}\n합쳐서 전체 줄거리 요약해줘."
    new_summary = self.ai.generate(summary_prompt)
    
    self.manager.update_world_and_summary(self.novel_id, new_world, new_summary)
    return chapter

  def _update_world(self, new_content, current_world):
    prompt = f"현재 세계관: {json.dumps(current_world, ensure_ascii=False)}\n새 내용: {new_content}\n분석해서 업데이트된 세계관을 JSON으로 반환해."
    result = self.ai.generate_json(prompt)
    try:
        return json.loads(result)
    except:
        return current_world