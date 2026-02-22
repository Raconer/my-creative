from typing import Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import Text, func
from models.novel import Novel
from models.prompt import PromptSetting
from models.chapter import Chapter
from models.generation_log import GenerationLog
from models.episode import Episode  # 에피소드 모델 추가
from schemas.novel import NovelCreate
from fastapi import Depends
from database import get_db 

class NovelService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    # ---------------------------------------------------------
    # 📝 소설 생성 및 관리
    # ---------------------------------------------------------
    def create_novel(self, novel_in: NovelCreate) -> Novel:
        """새로운 소설 프로젝트를 생성하고 기본 프롬프트를 초기화합니다."""
        db_novel = Novel(
            title=novel_in.title,
            genre=novel_in.genre,
            world_setting=novel_in.initial_world,
            rules=novel_in.initial_rules,
            story_summary=novel_in.description
        )
        self.db.add(db_novel)
        self.db.flush() 

        # 🚀 [업그레이드 완료] 기존의 강력했던 웹소설 프롬프트를 DB 템플릿으로 이식
        db_prompt = PromptSetting( novel_id=db_novel.id,
                            # 1. 플롯 생성 프롬프트: [전략적 사건 설계와 뽕맛 주입]
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

                            # 2. 본문 작성 프롬프트: [극강의 연출과 모바일 가독성]
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

                            # 3. 비평/평가 프롬프트: [독설가 편집장의 송곳 검수]
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

                            # 4. 요약 프롬프트: [맥락 보존과 떡밥 관리]
                            summary_prompt="""당신은 이야기의 모든 복선을 기억하는 기록관입니다. 
                            이번 화의 핵심 정보를 요약하여 다음 화의 기초를 닦으세요.

                            [입력 데이터]: {summary} + {content}

                            [갱신 형식]
                            1. 사건 요약: 핵심 진행 상황 (1~2문장)
                            2. 공학/설정 업데이트: 새로 등장한 장치나 밝혀진 과학적 사실
                            3. 인물 상태: 주인공에 대한 주변의 평판(착각도) 변화
                            4. 유보된 복선: 다음 화에서 반드시 해결하거나 언급해야 할 '떡밥' 리스트"""
                        )
        self.db.add(db_prompt)
        self.db.commit()
        self.db.refresh(db_novel)
        return db_novel

    def get_novel(self, novel_id: int) -> Optional[Novel]:
        """소설 ID로 소설 정보를 가져옵니다."""
        return self.db.query(Novel).filter(Novel.id == novel_id).first()

    # ---------------------------------------------------------
    # 🔍 검색 로직 (통합 검색 및 에피소드 검색)
    # ---------------------------------------------------------
    def search_content(self, keyword: Optional[str] = None) -> List[Novel]:
        """제목, 줄거리, 세계관 JSON 내부 텍스트까지 통합 검색합니다."""
        query = self.db.query(Novel)
        if keyword:
            filter_stmt = Novel.title.ilike(f"%{keyword}%") | Novel.story_summary.ilike(f"%{keyword}%")
            # JSON 데이터를 Text로 캐스팅하여 키워드 탐색
            filter_stmt |= Novel.world_setting.cast(Text).ilike(f"%{keyword}%")
            query = query.filter(filter_stmt)
        return query.all()

    def search_novels(self, title: Optional[str] = None, genre: Optional[str] = None) -> List[Novel]:
        """제목 또는 장르로 소설 리스트를 필터링합니다."""
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
        """가장 최근 회차 번호를 가져옵니다."""
        last = self.db.query(Chapter).filter(Chapter.novel_id == novel_id).order_by(Chapter.chapter_num.desc()).first()
        return int(last.chapter_num) if last else 0 # type: ignore

    def get_recent_context(self, novel_id: int, count: int = 3) -> str:
        """직전 회차들의 원고를 가져와 AI에게 문맥(Context)으로 제공합니다."""
        chapters = self.db.query(Chapter).filter(Chapter.novel_id == novel_id).order_by(Chapter.chapter_num.desc()).limit(count).all()
        chapters.reverse() # 시간순 정렬
        return "".join([f"\n[Chapter {c.chapter_num}]\n{c.content}\n" for c in chapters])

    # ---------------------------------------------------------
    # 💾 기록 및 저장 (Score 컬럼 반영)
    # ---------------------------------------------------------
    def log_attempt(self, novel_id: int, chapter_num: int, attempt: int, content: str, review: dict, is_selected: bool):
        """AI의 모든 시도 과정을 기록합니다 (시각화용 점수 포함)."""
        log = GenerationLog(
            novel_id=novel_id,
            chapter_num=chapter_num,
            attempt_num=attempt,
            content=content,
            score=int(review.get("score", 0)), # 정수형 점수 저장
            feedback=review.get("feedback", ""),
            raw_review=review,
            is_selected=1 if is_selected else 0
        )
        self.db.add(log)
        self.db.commit()

    def save_chapter(self, novel_id: int, chapter_num: int, content: str, score: int, feedback: str):
        """검수를 통과한 최종 원고를 저장합니다."""
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
        """세계관 데이터와 전체 줄거리 요약을 갱신합니다."""
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
        """모든 생성 로그를 최신순으로 가져옵니다."""
        return self.db.query(GenerationLog).filter(GenerationLog.novel_id == novel_id).order_by(GenerationLog.created_at.desc()).all()