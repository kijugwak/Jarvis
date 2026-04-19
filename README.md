# Jarvis

로컬 Ollama 기반 개인 비서 프로젝트입니다.

현재 기본 운영 모드는 **Siri-only** 입니다.
- 항상 듣는 daemon 없음
- Siri 단축어로 명령을 전달할 때만 실행

## 빠른 시작

```bash
cd /Users/gwaggiju/Jarvis
brew install ollama ffmpeg portaudio
/opt/homebrew/bin/python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
brew services start ollama
ollama pull qwen2.5:7b-instruct
```

## 현재 권장 사용법 (Siri-only)

### 1) 준비 인사 (Siri 단축어: `자비스 불러줘`)
```bash
cd /Users/gwaggiju/Jarvis && ./scripts/siri_jarvis.sh start
```

- 항상 듣기 모드를 끄고 Siri-only 상태로 전환
- 영어 인사 음성 출력

### 2) 실제 명령 전달 (Siri 단축어: `자비스 실행`)
```bash
cd /Users/gwaggiju/Jarvis && ./scripts/siri_jarvis.sh ask "오늘 뉴스 보여줘"
```

- 입력 문장을 1회 처리
- 라우터(`app/tools.py`)가 먼저 빠르게 처리하고
- 해당 안 되면 RAG + LLM 경로로 처리

### 3) 중지
```bash
cd /Users/gwaggiju/Jarvis && ./scripts/siri_jarvis.sh stop
```

## Siri 단축어 추천 구성

### 단축어 A: `자비스 불러줘`
- 액션: `셸 스크립트 실행`
- 스크립트:
```bash
cd /Users/gwaggiju/Jarvis && ./scripts/siri_jarvis.sh start
```

### 단축어 B: `자비스 실행`
- 액션 1: `입력 요청` (텍스트 또는 음성 받아오기)
- 액션 2: `셸 스크립트 실행`
- 스크립트:
```bash
cd /Users/gwaggiju/Jarvis && ./scripts/siri_jarvis.sh ask "$1"
```
- 셸 스크립트 입력을 첫 번째 인자로 전달하도록 설정

## 즉시 실행 라우터 (LLM 전 처리)

`app/tools.py`에서 다음 요청은 즉시 처리됩니다.
- 시간/상태 질의
- 뉴스 (`오늘 뉴스`)
- 사이트 열기 (`유튜브 열어줘`, `깃허브 열어줘`)
- 검색 (`AI 에이전트 검색해줘`)
- 앱 실행 (`터미널 실행해줘`)

## 뉴스 읽기 규칙

- 화면 출력: 제목/시간/링크 표시
- 음성 출력: URL과 시간 제거, 핵심 텍스트만 발화

## 선택 모드: 항상 듣는 daemon (옵션)

기본은 꺼져 있습니다. 필요할 때만 사용:
```bash
cd /Users/gwaggiju/Jarvis
./scripts/install_launch_agent.sh daemon "MacBook Pro 마이크" "Daniel" "165"
launchctl kickstart -k gui/$(id -u)/com.gwaggiju.jarvis
```

종료:
```bash
cd /Users/gwaggiju/Jarvis && ./scripts/siri_jarvis.sh stop
```

## 로그

```bash
tail -f ~/Library/Logs/jarvis.out.log
tail -f ~/Library/Logs/jarvis.err.log
```

## 주요 파일

```text
app/
  siri_one_shot.py   # Siri 전달 명령 1회 실행
  tools.py           # 의도 라우터 (LLM 전 처리)
  chat.py            # tool -> rag -> llm 처리 파이프라인
  brain.py           # Ollama 호출
  tts.py             # TTS + 음성용 텍스트 정리
  wake_daemon.py     # (옵션) 항상 듣는 모드
scripts/
  siri_jarvis.sh     # Siri 연동 진입점
  install_launch_agent.sh
  enroll_voice.py
```
