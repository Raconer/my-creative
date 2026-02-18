# 🖋️ My Creative Archive (노드 기반 창작 관리 시스템)

> **아이디어의 파생 과정을 시각화하고, 나만의 프롬프트 자산을 체계적으로 관리하는 로컬 전용 창작 스페이스입니다.**

---

## 🌟 핵심 기능 (Key Features)

* **Visual History (Git-Style):** 소설이나 기획안이 발전하는 과정을 트리 구조로 시각화합니다.
* **Branching:** 특정 아이디어에서 여러 갈래의 답변을 유도하고 비교할 수 있습니다.
* **Prompt DB:** 성공적이었던 프롬프트를 저장하고 태그별로 관리합니다.
* **Local Secure:** 모든 데이터는 본인의 컴퓨터(SQLite & Markdown)에만 안전하게 저장됩니다.

---

## 🛠️ 기술 스택 (Tech Stack)

### **Backend**
* **Framework:** FastAPI (Python 3.10+)
* **Database:** SQLite (SQLAlchemy ORM)
* **Storage:** Local Markdown Files (`.md`)

### **Frontend**
* **Library:** React.js
* **Visualization:** React Flow (노드 기반 그래프 라이브러리)
* **Styling:** Tailwind CSS (예정)

---

## 📂 프로젝트 구조 (Structure)

```text
my-creative/
├── backend/             # FastAPI 서버 및 DB 로직
│   ├── storage/         # 생성된 마크다운 결과물 저장소
│   ├── main.py          # API 엔드포인트
│   ├── models.py        # DB 스키마 정의
│   └── database.py      # SQLite 연결 설정
├── frontend/            # React 시각화 대시보드
│   └── src/             # React 소스 코드
├── .gitignore           # macOS/VSCode/Python/Node 제외 설정
└── README.md            # 프로젝트 가이드 (현재 파일)
```

---

## 🚀 시작하기 (Getting Started)

### **1. 사전 준비**
* [Python 3.10+](https://www.python.org/) 설치
* [Node.js LTS](https://nodejs.org/) 설치

### **2. 백엔드 실행**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

* API 서버 주소: http://127.0.0.1:8000
* 문서(Swagger): http://127.0.0.1:8000/docs

### **3. 프런트엔드 실행**
```bash
cd frontend
npm install
npm start
```

* 웹 인터페이스 주소: http://localhost:3000

## 📝 라이선스 (License)
> 개인 사용 및 학습용 프로젝트입니다.