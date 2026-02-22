import json
import time
from typing import Dict, Any
from sqlalchemy.orm import Session
from models.chapter import Chapter
from models.generation_log import GenerationLog
from models.novel import Novel
from core.ai_driver import AIDriver
from service.novel_service import NovelService


def safe_format_prompt(template: str, kwargs: dict) -> str:
    """JSON 중괄호와 프롬프트 변수 중괄호의 충돌을 방지하는 안전한 포맷터"""
    result = template
    for key, value in kwargs.items():
        result = result.replace(f"{{{key}}}", str(value))
    return result

class NovelGenerator:
    def __init__(self, db: Session, novel_id: int):
        self.db = db
        self.novel_id = novel_id
        self.ai = AIDriver()

    def run_daily_routine(self, config_dict: Dict[str, Any]):
        # 1. 데이터 로드 (DB에서 로드)
        novel = self.db.query(Novel).filter(Novel.id == self.novel_id).first()
        if not novel or not novel.prompts: 
            print("⚠️ 소설 정보 또는 프롬프트 설정이 없습니다.")
            return False
        
        p = novel.prompts
        
        last = self.db.query(Chapter).filter(Chapter.novel_id == self.novel_id).order_by(Chapter.chapter_num.desc()).first()
        current_chapter_num=  int(last.chapter_num) if last else 0 # type: ignore
        
        print(f"\n📅 [진행상황] 제 {current_chapter_num}화 작성을 시작합니다.")

        # 2. 문맥 확보 및 재료 준비
        count = 10
        chapters = self.db.query(Chapter).filter(Chapter.novel_id == self.novel_id).order_by(Chapter.chapter_num.desc()).limit(count).all()
        chapters.reverse() # 시간순 정렬
        recent_context = "".join([f"\n[Chapter {c.chapter_num}]\n{c.content}\n" for c in chapters])
        
        overall_summary = novel.story_summary or "이야기의 시작"
        
        rules_dict = novel.rules if isinstance(novel.rules, dict) else {}
        prompt_kwargs = {
            "chapter_num": current_chapter_num,
            "title": novel.title,
            "summary": overall_summary,
            "world": json.dumps(novel.world_setting, ensure_ascii=False),
            "rules_json": json.dumps(novel.rules, ensure_ascii=False),
            "context": recent_context,
            **rules_dict
        }

        # 3. 플롯 생성
        print("💡 이번 화의 플롯을 구상 중...")
        plot_p = safe_format_prompt(p.plot_prompt, prompt_kwargs)
        plot_plan = self.ai.generate(plot_p)
        print(f"   ▶ 계획: {plot_plan[:100]}...")
        prompt_kwargs["plot"] = plot_plan

        # 4. 작성 및 평가 루프 (기본 10회)
        best_score = 0
        best_content = ""
        best_feedback = "점수 미달"
        current_feedback = None 
        
        max_attempts = config_dict.get("max_attempts", 10)
        min_score = config_dict.get("min_score", 95)

        for attempt in range(1, max_attempts + 1):
            print(f"\n🔄 [시도 {attempt}/{max_attempts}] 작성 중... (이전 피드백: {current_feedback if current_feedback else '없음'})")
            
            # 작성 프롬프트 구성 (피드백 주입)
            write_p = safe_format_prompt(p.writing_prompt, prompt_kwargs)
            if current_feedback:
                write_p += f"\n\n🚨 [재작성 지시사항] 🚨\n이전 원고가 반려되었습니다. 이유: \"{current_feedback}\"\n이번 원고에서는 이를 반드시 수정하세요."
            
            content = self.ai.generate(write_p)
            
            # 내용 길이 체크 (기존 로직 유지)
            if not content or len(content) < 500:
                print("   ⚠️ 내용 부족(500자 미만) 재시도")
                continue
            
            # 평가 단계
            prompt_kwargs["content"] = content
            review_p = safe_format_prompt(p.review_prompt, prompt_kwargs)
            review_json = self.ai.generate_json(review_p)
            
            try:
                review_data = json.loads(review_json)
                score = int(review_data.get("score", 0))
                current_feedback = review_data.get("feedback", "피드백 없음")
                
                print(f"   ⭐ 점수: {score}점")
                print(f"   💬 비평: {current_feedback}")

                # 로그 기록 (DB 저장)
                is_selected = (score >= min_score)
                
                """AI의 모든 시도 과정을 기록합니다 (시각화용 점수 포함)."""
                log = GenerationLog(
                    novel_id=self.novel_id,
                    chapter_num=current_chapter_num,
                    attempt_num=attempt,
                    content=content,
                    score=int(review_data.get("score", 0)), # 정수형 점수 저장
                    feedback=review_data.get("feedback", ""),
                    raw_review=review_data,
                    is_selected=1 if is_selected else 0
                )
                self.db.add(log)
                self.db.commit()
                

                # 최고 점수 갱신
                if score > best_score:
                    best_score = score
                    best_content = content
                    best_feedback = current_feedback

                # 통과 조건
                if is_selected:
                    print(f"✅ 통과! ({score}점)")
                    break
                    
            except Exception as e:
                print(f"   ⚠️ 평가 오류: {e}")
                current_feedback = "JSON 출력 형식을 지키고 점수를 포함하세요."
                continue

        # 5. 최종 결과 처리
        if best_content:
            
            """검수를 통과한 최종 원고를 저장합니다."""
            db_chapter = Chapter(
                novel_id=self.novel_id, 
                chapter_num=current_chapter_num, 
                content=best_content, # 💡 주의: 루프 안의 content가 아니라 best_content를 저장해야 합니다.
                score=best_score,     # 💡 score -> best_score
                feedback=best_feedback
            )
            self.db.add(db_chapter)
            self.db.commit()
            
            # 줄거리 요약 및 범용 설정 갱신
            print("📑 전체 줄거리 요약 및 설정 갱신 중...")
            prompt_kwargs["content"] = best_content 
            summary_p = safe_format_prompt(p.summary_prompt, prompt_kwargs)
            
            novel = self.db.query(Novel).filter(Novel.id == self.novel_id).first()
            if not novel:
                print("❌ 소설을 찾을 수 없습니다.")
                return False

            try:
                # 🚀 1. AI 응답을 JSON 구조로 받습니다. (장르 무관 범용 파싱)
                summary_json_str = self.ai.generate_json(summary_p)
                summary_data = json.loads(summary_json_str)

                # 🚀 2. 범용 변수명 사용: summary(요약)와 updated_settings(설정 갱신)
                new_summary = summary_data.get("summary", novel.story_summary)
                new_settings = summary_data.get("updated_settings", novel.world_setting)

            except Exception as e:
                # 🚀 3. AI가 JSON 형식을 어겼을 때의 Fallback (JPA의 try-catch 롤백 방지 역할)
                print(f"⚠️ 요약 파싱 실패, 텍스트 전체를 요약으로 대체합니다: {e}")
                fallback_text = self.ai.generate(summary_p)
                new_summary = fallback_text[:1000] # 너무 길면 잘라냄
                new_settings = novel.world_setting # 파싱 실패 시 기존 설정 유지

            # 4. DB 업데이트 
            novel.world_setting = new_settings   # type: ignore (범용 상태 저장소로 활용)
            novel.story_summary = new_summary    # type: ignore
            
            self.db.commit()
            self.db.refresh(novel)
            
            print(f"🏁 [{novel.title}] 제 {current_chapter_num}화 집필 완료! (최종점수: {best_score})")
            
            return True
        else:
            print(f"\n❌ 모든 시도 실패. 유효한 원고를 생성하지 못했습니다.")
            return False