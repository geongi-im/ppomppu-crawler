# 📱 PPomPPu Crawler

뽐뿌 커뮤니티의 휴대폰 관련 게시글을 자동으로 크롤링하고, AI로 분석하여 핵심 딜 정보만 텔레그램으로 전송하는 자동화 봇입니다.

## 🚀 주요 기능

- **자동 크롤링**: 뽐뿌 휴대폰 게시판에서 키워드 기반 게시글 수집
- **AI 요약**: Google Gemini AI를 활용한 게시글 내용 분석 및 딜 정보 추출
- **중복 방지**: SQLite 데이터베이스를 통한 중복 게시글 관리
- **텔레그램 알림**: 요약된 딜 정보를 텔레그램으로 자동 전송
- **로깅 시스템**: 상세한 로그 기록 및 모니터링

## 📋 추출 정보

각 게시글에서 다음 정보를 자동으로 추출합니다:

- **통신사**: SKT / KT / LGU+ / MVNO
- **거래유형**: 번호이동 / 기기변경 / 자급제
- **기기명 및 저장용량**
- **요금제명**
- **월 납부액**
- **할부원금**
- **현금완납가**
- **부가서비스 정보**
- **실구매가 계산**

## 🛠️ 기술 스택

- **Python 3.8+**
- **BeautifulSoup4**: 웹 크롤링
- **Google Gemini AI**: 게시글 요약 및 분석
- **SQLite**: 데이터베이스 관리
- **Telegram Bot API**: 알림 전송
- **Python-dotenv**: 환경변수 관리

## 📦 설치 및 설정

### 1. 저장소 클론
```bash
git clone https://github.com/your-username/ppomppu-crawler.git
cd ppomppu-crawler
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정
`.env` 파일을 생성하고 다음 정보를 입력하세요:

```env
# 검색 키워드 (예: 폴드7, 아이폰15 등)
SEARCH_KEYWORD=폴드7

# Google Gemini API 키
GEMINI_API_KEY=your_gemini_api_key_here

# 텔레그램 봇 설정
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
TELEGRAM_CHAT_TEST_ID=your_test_chat_id_here
```

### 4. 텔레그램 봇 설정
1. [@BotFather](https://t.me/botfather)에서 봇 생성
2. 봇 토큰을 `TELEGRAM_BOT_TOKEN`에 설정
3. 채팅방 ID를 `TELEGRAM_CHAT_ID`에 설정

## 🚀 사용법

### 기본 실행
```bash
python main.py
```

### 개별 모듈 테스트
```bash
# 크롤러 테스트
python crawler.py

# 데이터베이스 테스트
python database.py

# 요약기 테스트
python summarizer.py
```

## 📁 프로젝트 구조

```
ppomppu-crawler/
├── main.py              # 메인 실행 파일
├── crawler.py           # 뽐뿌 크롤링 모듈
├── database.py          # SQLite 데이터베이스 관리
├── summarizer.py        # AI 요약 모듈
├── requirements.txt     # Python 의존성
├── system_prompt.md     # AI 시스템 프롬프트
├── user_prompt.md       # AI 사용자 프롬프트
├── logs/                # 로그 파일 저장소
└── utils/
    ├── telegram_util.py # 텔레그램 유틸리티
    ├── logger_util.py   # 로깅 유틸리티
    └── api_util.py      # API 유틸리티
```

## 🔧 주요 모듈 설명

### Crawler (`crawler.py`)
- 뽐뿌 웹사이트 크롤링
- 게시글 제목, URL, 작성일시 추출
- 본문 내용 파싱

### Database (`database.py`)
- SQLite 데이터베이스 관리
- 중복 게시글 방지
- 전송 상태 추적

### Summarizer (`summarizer.py`)
- Google Gemini AI 연동
- 게시글 내용 분석 및 요약
- 딜 정보 구조화

### Telegram Util (`utils/telegram_util.py`)
- 텔레그램 봇 API 연동
- 메시지 전송 기능
- 이미지 전송 지원

## 📊 로그 시스템

- **로그 위치**: `logs/` 디렉토리
- **로그 형식**: `YYYY-MM-DD_log.log`
- **로그 레벨**: DEBUG, INFO, WARNING, ERROR
- **출력**: 콘솔 + 파일 동시 출력

## 🔄 실행 흐름

1. **크롤링**: 뽐뿌에서 키워드 기반 게시글 수집
2. **중복 확인**: 데이터베이스에서 기존 게시글과 비교
3. **AI 요약**: 새로운 게시글만 AI로 분석
4. **텔레그램 전송**: 요약된 딜 정보 전송
5. **상태 업데이트**: 전송 완료 상태로 마킹

## ⚠️ 주의사항

- 뽐뿌 웹사이트의 구조 변경 시 크롤러 수정 필요
- Google Gemini API 사용량 및 비용 고려
- 텔레그램 봇 API 제한사항 확인
- 웹 크롤링 시 서버 부하 고려
