import json
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
from models.chapter import Chapter
from models.generation_log import GenerationLog
from models.novel import Novel
from core.ai_driver import AIDriver

def safe_format_prompt(template: str, kwargs: dict) -> str:
    result = template
    for key, value in kwargs.items():
        result = result.replace(f"{{{key}}}", str(value))
    return result

class NovelGenerator:
    def __init__(self, db: Session, novel_id: int):
        self.db = db
        self.novel_id = novel_id
        self.ai = AIDriver()

    def run_daily_routine(self, config_dict: Dict[str, Any]) -> bool:
        """메인 워크플로우"""
        print(f"\n🚀 [소설 ID: {self.novel_id}] AI 작가 에이전트 구동 시작...")

        novel = self.db.query(Novel).filter(Novel.id == self.novel_id).first()
        if not novel or not novel.prompts: 
            print("❌ [중단] 소설 정보 또는 프롬프트 설정이 없습니다.")
            return False
        
        current_chapter_num = self._get_next_chapter_num()
        prompt_kwargs = self._build_context_kwargs(novel, current_chapter_num)

        # 1. 플롯 생성
        print(f"📅 [진행상황] 제 {current_chapter_num}화 플롯 구상 중...")
        plot_p = safe_format_prompt(novel.prompts.plot_prompt, prompt_kwargs)
        prompt_kwargs["plot"] = self.ai.generate(plot_p)

        # 2. 작성 및 평가 루프
        min_score = config_dict.get("min_score", 95)
        # 성공적으로 기준을 넘었을 때만 데이터가 반환되도록 내부 로직 수정됨
        best_content, best_score, best_feedback = self._execute_generation_loop(
            novel, prompt_kwargs, config_dict, current_chapter_num
        )

        # 🚨 [핵심 체크] 기준 점수(min_score)를 넘지 못했다면 여기서 즉시 종료!
        if not best_content or best_score < min_score:
            print(f"\n⚠️ [최종 반려] 시도 횟수 내에 목표 점수({min_score}점)를 달성하지 못했습니다.")
            print(f"   (최고 기록: {best_score}점) - DB에 저장하지 않고 종료합니다.")
            return False

        # 3. 기준 통과 시에만 실행되는 저장 로직
        print(f"\n💾 [검수 통과] 최종 점수 {best_score}점으로 저장을 시작합니다!")
        self._save_chapter(current_chapter_num, best_content, best_score, best_feedback)
        self._update_novel_settings(novel, prompt_kwargs, best_content)

        self.db.commit()
        print(f"🏁 [완료] 제 {current_chapter_num}화 집필 및 갱신 성공!\n")
        return True

    def _execute_generation_loop(self, novel: Novel, prompt_kwargs: Dict[str, Any], config_dict: Dict[str, Any], current_chapter_num: int) -> Tuple[str, int, str]:
        """AI 집필 및 평가 반복 루프"""
        best_score, best_content, best_feedback = 0, "", "점수 미달"
        current_feedback = None 
        
        max_attempts = config_dict.get("max_attempts", 10)
        min_score = config_dict.get("min_score", 95)

        for attempt in range(1, max_attempts + 1):
            print(f"   🔄 [시도 {attempt}/{max_attempts}] 원고 작성 중...", end="\r")
            
            write_p = safe_format_prompt(novel.prompts.writing_prompt, prompt_kwargs)
            if current_feedback:
                write_p += f"\n\n🚨 [재작성 지시사항]\n{current_feedback}"
            
            content = self.ai.generate(write_p)
            if not content or len(content) < 500: continue
            
            prompt_kwargs["content"] = content
            review_p = safe_format_prompt(novel.prompts.review_prompt, prompt_kwargs)
            
            try:
                review_data = json.loads(self.ai.generate_json(review_p))
                score = int(review_data.get("score", 0))
                current_feedback = review_data.get("feedback", "피드백 없음")
            except Exception:
                review_data, score, current_feedback = {}, 0, "평가 파싱 오류"

            # 로그 DB 저장 (모든 시도는 기록에 남김)
            self.db.add(GenerationLog(
                novel_id=self.novel_id, chapter_num=current_chapter_num,
                attempt_num=attempt, content=content, score=score,
                feedback=current_feedback, raw_review=review_data,
                is_selected=1 if score >= min_score else 0
            ))
            self.db.commit()

            print(f"   🧐 [시도 {attempt}] 점수: {score}점 {'✅' if score >= min_score else '❌'}")

            # 목표 점수 달성 시 즉시 반환
            if score >= min_score:
                return content, score, current_feedback
            
            # 기준은 못 넘었지만 이전보다 점수가 높으면 일단 '임시 베스트'로 간주
            if score > best_score:
                best_score, best_content, best_feedback = score, content, current_feedback

        # 루프가 끝날 때까지 min_score를 못 넘었다면, 
        # 위쪽 run_daily_routine에서 걸러낼 수 있도록 '빈 값'을 섞어서 반환
        return "", best_score, best_feedback

    # ----------------------------------------------------------------
    # (나머지 헬퍼 함수들 _get_next_chapter_num, _save_chapter 등은 동일)
    # ----------------------------------------------------------------
    def _get_next_chapter_num(self) -> int:
        last_chapter = self.db.query(Chapter).filter(Chapter.novel_id == self.novel_id).order_by(Chapter.chapter_num.desc()).first()
        return int(getattr(last_chapter, "chapter_num")) + 1 if last_chapter else 1

    def _build_context_kwargs(self, novel: Novel, current_chapter_num: int) -> Dict[str, Any]:
        chapters = self.db.query(Chapter).filter(Chapter.novel_id == self.novel_id).order_by(Chapter.chapter_num.desc()).limit(10).all()
        recent_context = "".join([f"\n[Chapter {c.chapter_num}]\n{c.content}\n" for c in reversed(chapters)])
        rules_dict = novel.rules if isinstance(novel.rules, dict) else {}
        return {
            "chapter_num": current_chapter_num, "title": novel.title,
            "summary": novel.story_summary or "이야기의 시작",
            "world": json.dumps(novel.world_setting, ensure_ascii=False),
            "rules_json": json.dumps(rules_dict, ensure_ascii=False),
            "context": recent_context, **rules_dict
        }

    def _save_chapter(self, chapter_num: int, content: str, score: int, feedback: str):
        self.db.add(Chapter(novel_id=self.novel_id, chapter_num=chapter_num, content=content, score=score, feedback=feedback))

    def _update_novel_settings(self, novel: Novel, prompt_kwargs: Dict[str, Any], best_content: str):
        prompt_kwargs["content"] = best_content 
        summary_p = safe_format_prompt(novel.prompts.summary_prompt, prompt_kwargs)
        try:
            summary_data = json.loads(self.ai.generate_json(summary_p))
            novel.story_summary = summary_data.get("summary", novel.story_summary) # type: ignore
            novel.world_setting = summary_data.get("updated_settings", novel.world_setting) # type: ignore
        except Exception:
            fallback_text = self.ai.generate(summary_p)
            if fallback_text: novel.story_summary = fallback_text[:1000] # type: ignore