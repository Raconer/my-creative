from typing import Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import Text
from fastapi import Depends
from database import get_db 
from models.novel import Novel
from models.prompt import PromptSetting
from models.chapter import Chapter
from models.generation_log import GenerationLog
from schemas.novel import NovelCreate

class NovelService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    # ---------------------------------------------------------
    # 📝 소설 생성 및 관리
    # ---------------------------------------------------------
    def create_novel(self, novel_in: NovelCreate) -> Novel:
        """새로운 소설 프로젝트 생성 및 기본 프롬프트 세팅"""
        db_novel = Novel(
            title=novel_in.title,
            genre=novel_in.genre,
            world_setting=novel_in.initial_world,
            rules=novel_in.initial_rules,
            story_summary=novel_in.description
        )
        self.db.add(db_novel)
        self.db.flush() # DB에 밀어넣어서 자동 생성된 ID 값을 받아옵니다.

        # 🚀 Pylance 에러 완벽 방어: getattr과 int 캐스팅으로 타입 안전성 확보
        novel_id = int(getattr(db_novel, "id"))
        
        # 프롬프트 생성 로직을 헬퍼 함수로 분리하여 가독성 확보
        db_prompt = self._build_default_prompt(novel_id)
        self.db.add(db_prompt)
        
        self.db.commit()
        self.db.refresh(db_novel)
        return db_novel

    def get_novel(self, novel_id: int) -> Optional[Novel]:
        return self.db.query(Novel).filter(Novel.id == novel_id).first()

    # ---------------------------------------------------------
    # 🔍 검색 로직 
    # ---------------------------------------------------------
    def search_content(self, keyword: Optional[str] = None) -> List[Novel]:
        """제목, 줄거리, 세계관(JSON 텍스트 변환) 통합 검색"""
        query = self.db.query(Novel)
        if keyword:
            filter_stmt = (
                Novel.title.ilike(f"%{keyword}%") | 
                Novel.story_summary.ilike(f"%{keyword}%") |
                Novel.world_setting.cast(Text).ilike(f"%{keyword}%")
            )
            query = query.filter(filter_stmt)
        return query.all()

    def search_novels(self, title: Optional[str] = None, genre: Optional[str] = None) -> List[Novel]:
        query = self.db.query(Novel)
        if title:
            query = query.filter(Novel.title.ilike(f"%{title}%"))
        if genre:
            query = query.filter(Novel.genre.ilike(f"%{genre}%"))
        return query.all()

    # ---------------------------------------------------------
    # ✍️ 집필 프로세스 지원 로직
    # ---------------------------------------------------------
    def get_last_chapter_num(self, novel_id: int) -> int:
        last = self.db.query(Chapter).filter(Chapter.novel_id == novel_id).order_by(Chapter.chapter_num.desc()).first()
        return int(getattr(last, "chapter_num")) if last else 0  # Pylance 에러 방어

    def get_recent_context(self, novel_id: int, count: int = 3) -> str:
        chapters = self.db.query(Chapter).filter(Chapter.novel_id == novel_id).order_by(Chapter.chapter_num.desc()).limit(count).all()
        return "".join([f"\n[Chapter {c.chapter_num}]\n{c.content}\n" for c in reversed(chapters)])

    # ---------------------------------------------------------
    # 💾 기록 및 저장
    # ---------------------------------------------------------
    def log_attempt(self, novel_id: int, chapter_num: int, attempt: int, content: str, review: dict, is_selected: bool):
        self.db.add(GenerationLog(
            novel_id=novel_id,
            chapter_num=chapter_num,
            attempt_num=attempt,
            content=content,
            score=int(review.get("score", 0)),
            feedback=review.get("feedback", ""),
            raw_review=review,
            is_selected=1 if is_selected else 0
        ))
        self.db.commit()

    def save_chapter(self, novel_id: int, chapter_num: int, content: str, score: int, feedback: str) -> Chapter:
        db_chapter = Chapter(
            novel_id=novel_id, 
            chapter_num=chapter_num, 
            content=content, 
            score=score, 
            feedback=feedback
        )
        self.db.add(db_chapter)
        self.db.commit()
        return db_chapter

    def update_world_and_summary(self, novel_id: int, new_world: Any, new_summary: str):
        novel = self.get_novel(novel_id)
        if novel:
            novel.world_setting = new_world   # type: ignore
            novel.story_summary = new_summary # type: ignore
            self.db.commit()
            self.db.refresh(novel)

    # ---------------------------------------------------------
    # 📊 히스토리 조회
    # ---------------------------------------------------------
    def get_history(self, novel_id: int):
        return self.db.query(GenerationLog).filter(GenerationLog.novel_id == novel_id).order_by(GenerationLog.created_at.desc()).all()

    # ---------------------------------------------------------
    # 🛠️ 프라이빗 헬퍼 메서드
    # ---------------------------------------------------------
    def _build_default_prompt(self, novel_id: int) -> PromptSetting:
        """기본 프롬프트 템플릿을 생성합니다."""
        return PromptSetting(
            novel_id=novel_id,
            # 💡 [1단계] 플롯 설계 프롬프트
            # 역할: 이번 회차의 기승전결 스토리라인, 핵심 사건, 캐릭터의 행동 방향을 기획합니다.
            plot_prompt="""당신은 유료 연독률 1위, 문피아/카카오페이지의 전설적인 스타 PD입니다. 
                            제 {chapter_num}화의 플롯을 '다음 화 결제'를 하지 않으면 미칠 것 같은 호흡으로 설계하세요.

                            [핵심 소스]
                            - 세계관 및 주인공: {world}
                            - 설정/규칙: {rules_json}
                            - 직전 상황 요약: {summary}

                            [★ 흥행 공식 4단계 플롯 설계]
                            1. [기 - 결핍과 위기]: 주인공의 자원이 부족하거나 주변의 압박이 최고조에 달함. 공학적 해결책을 위한 '빌드업(노가다)' 시작. (독자가 "과연 될까?" 의심하게 할 것)
                            2. [승 - 갈등의 심화]: 무능한 조연 혹은 악역의 노골적인 방해. 주인공의 계획이 수포로 돌아갈 것 같은 찰나의 절망감 부여.
                            3. [전 - 카타르시스 폭발]: 준비한 공학 기믹이 발동. '보여주기(Showing)' 기법으로 압도적인 물리적 현상 묘사. 조연들이 "저게 마법이 아니라고?"라며 경악하는 '착각 요소' 극대화.
                            4. [결 - 보상과 갈고리]: 주인공의 덤덤한 승리 선언. 하지만 마지막에 예상치 못한 더 큰 위기나 새로운 미스터리를 던지는 '절단신공(Cliffhanger)'.

                            [추가 필수 사항]
                            - 이번 화에 적용될 '공학적 기믹'의 논리적 단계를 3단계로 명시하세요.
                            - 조연들의 리액션 변화(비웃음 -> 의심 -> 경악 -> 숭배)를 포함하세요.""",
            # 💡 [2단계] 본문 집필 프롬프트
            # 역할: 1단계에서 짠 플롯을 바탕으로, 실제 독자가 읽을 소설 본문(텍스트)을 가독성 좋게 작성합니다.
            writing_prompt="""당신은 회당 조회수 100만의 괴물 작가입니다. 
                            편집장의 까다로운 채점 기준(95점)을 비웃듯 완벽한 '마스터피스'를 출력하세요.

                            ### 📱 [웹소설 전용 가독성 규칙]
                            - 1문단 1~3줄 원칙: 스마트폰 화면 한 장에 여백이 충분해야 합니다.
                            - 지문과 대화의 황금비: 대화 6, 서술 4. 대화문 앞뒤로 엔터를 쳐서 호흡을 조절하세요.
                            - 단문 위주: "했다. 그랬다." 식의 간결하고 힘 있는 문체. 수식어 자제.

                            ### 🎭 [연출 및 캐릭터 가이드]
                            - Telling 금지, Showing 집중: "놀랐다"고 쓰지 말고 "동공이 지진이라도 난 듯 떨렸다"고 쓰세요.
                            - 주인공 강춘명: 감정을 낭비하지 마세요. "귀찮네.", "계산대로군." 같은 건조한 매력 유지.
                            - 공학적 뽕맛: 기계 작동음(위이잉, 철컥)과 물리적 수치(압력 500psi, 오차 0.01mm)를 섞어 전문성을 높이세요.

                            ### 🎬 [집필 재료 및 제약]
                            - 플롯: {plot} / 맥락: {context} / 설정: {world} {rules_json}
                            - 분량: 4,500자 내외 (공백 포함)

                            [★ 95점 돌파 특수 명령]: 마지막 문장은 독자가 "아, 여기서 끊는 게 어딨어!"라고 소리칠 만큼 결정적인 순간에 멈추세요.""",
                            
            # 💡 [3단계] 검수 및 평가 프롬프트
            # 역할: 2단계에서 작성된 원고를 냉정하게 채점하고, 목표 점수 미달 시 재작성을 위한 피드백(수정 지시)을 내립니다.
            review_prompt="""당신은 작가의 자존심을 짓밟아서라도 최고의 글을 뽑아내는 악마 편집장입니다. 
                            독자의 눈으로 원고를 난도질하고, 95점 미만은 무조건 재집필을 명령하세요.

                            [소설 본문]
                            {content}

                            [★ 채점 기준표 (각 20점)]
                            1. 가독성: 벽돌 문단이 있는가? 대화문이 답답하지 않은가?
                            2. 사이다(뽕맛): 조연들의 경악 리액션이 소름 돋게 묘사되었는가?
                            3. 개연성: 공학적 해결책이 '말장난'이 아니라 '논리적'으로 들리는가?
                            4. 캐릭터: 주인공이 일반인처럼 굴지 않고 공학도 특유의 광기를 유지하는가?
                            5. 절단신공: 마지막 장면이 결제를 부르는가?

                            [출력 가이드] 반드시 JSON으로만 응답할 것.
                            - 90점 미만이면 피드백에 "구체적으로 어느 문장을 삭제/수정할지" 명령하세요.
                            - 점수는 엄격하게 매기되, details의 합이 score가 되어야 합니다.

                            {
                            "details": {"readability": 0, "catharsis": 0, "structure": 0, "character": 0, "fun": 0},
                            "score": 0,
                            "reason": "독자 반응 예측을 포함한 냉정한 평가",
                            "feedback": "작가의 뇌를 개조할 수준의 구체적 지시"
                            }""",

            # 💡 [4단계] 요약 및 동기화 프롬프트
            # 역할: 최종 통과된 원고를 분석하여 전체 줄거리를 갱신하고, 다음 화에 반영될 새로운 설정(떡밥, 인물 상태 등)을 DB에 저장합니다.
            summary_prompt="""당신은 이야기의 모든 복선을 기억하는 기록관입니다. 
                                이번 화의 핵심 정보를 요약하여 다음 화의 기초를 닦으세요.

                                [입력 데이터]: {summary} + {content}

                                [갱신 형식] 응답은 반드시 아래 JSON 형식을 지키세요:
                                {
                                "summary": "이번 화 핵심 요약 (1~2문장)",
                                "updated_settings": "새로 등장한 장치, 밝혀진 사실, 떡밥 등 추가되거나 변경된 세계관 정보"
                                }"""
        )