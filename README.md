# Jarvis

로컬에서 동작하는 저비용 음성 비서 프로젝트입니다.

## 목표

- 클라우드 LLM 없이 로컬 LLM(Ollama) 사용
- 음성 입력(STT) + 음성 출력(TTS)
- 간단한 자동화(아침 브리핑)
- 위험 작업 재확인 안전 장치

## 프로젝트 구조

```text
app/
  main.py          # 텍스트 모드 진입점
  voice_main.py    # 음성 모드 진입점
  brain.py         # Ollama 호출
  tools.py         # 로컬 즉시 실행 도구(크롬 열기, 시간 등)
  rag.py           # 지식 문서 검색
data/
  knowledge/       # 개인 지식 문서(.md/.txt)
scripts/
  morning_brief.py # 자동화 예시 스크립트
```

## 빠른 시작

1. 의존성 설치

```bash
brew install ollama ffmpeg portaudio
/opt/homebrew/bin/python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Ollama 실행 + 모델 준비

```bash
brew services start ollama
ollama pull qwen2.5:7b-instruct
```

3. CLI 실행

```bash
source .venv/bin/activate
python -m app.main
```

예시 입력:
- `안녕 자비스`
- `지금 몇시야`
- `chrome에서 naver 켜줘`

4. 음성 모드 실행

```bash
source .venv/bin/activate
python -m app.voice_main
```

## 원클릭 실행 스크립트 (음성 전용)

```bash
cd /Users/gwaggiju/Jarvis
./scripts/run_jarvis.sh menubar
./scripts/run_jarvis.sh voice
./scripts/run_jarvis.sh daemon
```

- `menubar`: 상단 `J` 아이콘. 텍스트 없이 음성 1회 듣기만 지원
- `voice`: 연속 음성 모드
- `daemon`: 항상 대기하다가 `자비스`/`jarvis`를 들으면 1회 명령 실행

핫워드 대기 시간/명령 녹음 시간은 환경변수로 조절할 수 있습니다.

```bash
export WAKE_LISTEN_SECONDS=2
export COMMAND_LISTEN_SECONDS=6
./scripts/run_jarvis.sh daemon
```

## 맥북 켤 때 자동 시작 (LaunchAgent)

```bash
cd /Users/gwaggiju/Jarvis
./scripts/install_launch_agent.sh
```

위 스크립트를 한 번 실행하면 로그인 시점에 Jarvis 데몬이 자동 시작됩니다.
기본 모드는 `menubar`(J 아이콘, 음성 전용)입니다.

```bash
./scripts/install_launch_agent.sh menubar
./scripts/install_launch_agent.sh daemon
```

중지/재시작:

```bash
launchctl unload ~/Library/LaunchAgents/com.gwaggiju.jarvis.plist
launchctl load ~/Library/LaunchAgents/com.gwaggiju.jarvis.plist
```

로그 확인:

```bash
tail -f ~/Library/Logs/jarvis.out.log
tail -f ~/Library/Logs/jarvis.err.log
```

## Siri 단축어 연동

Siri는 트리거 역할을 하고, 실제 작업은 Jarvis 스크립트가 수행합니다.

먼저 실행 권한:

```bash
cd /Users/gwaggiju/Jarvis
chmod +x ./scripts/siri_jarvis.sh
```

단축어 앱에서 아래 명령을 각각 `셸 스크립트 실행`으로 등록하세요.

1. `자비스 실행`

```bash
cd /Users/gwaggiju/Jarvis && ./scripts/siri_jarvis.sh start
```

2. `자비스 중지`

```bash
cd /Users/gwaggiju/Jarvis && ./scripts/siri_jarvis.sh stop
```

3. `자비스 브리핑`

```bash
cd /Users/gwaggiju/Jarvis && ./scripts/siri_jarvis.sh briefing
```

4. `자비스 업무 시작`

```bash
cd /Users/gwaggiju/Jarvis && ./scripts/siri_jarvis.sh work-start
```

상태 확인:

```bash
cd /Users/gwaggiju/Jarvis && ./scripts/siri_jarvis.sh status
```

## 가장 편한 운영 방식

개발/테스트할 때는 아래 순서가 가장 편합니다.

1. 터미널 1개: `cd /Users/gwaggiju/Jarvis && source .venv/bin/activate`
2. 텍스트 모드 먼저 검증: `python -m app.main`
3. 기능 확인 후 음성 모드: `python -m app.voice_main`
4. 지식 추가 시 `data/knowledge` 파일만 수정하고 바로 재질문

## RAG 지식 문서 넣기

`data/knowledge` 폴더에 `.md` 또는 `.txt` 파일을 넣으면, 질문 시 관련 문맥이 자동으로 검색되어 답변에 반영됩니다.

예시 파일:
- `/Users/gwaggiju/Jarvis/data/knowledge/profile.md`

추가 예시:

```md
# 답변 규칙
- 비용이 드는 제안은 항상 대안을 함께 제시
- 답변은 먼저 결론 1줄, 다음에 실행 단계
```

## 자동화 예시

```bash
crontab -e
```

평일 오전 8시:

```cron
0 8 * * 1-5 /Users/gwaggiju/Jarvis/.venv/bin/python /Users/gwaggiju/Jarvis/scripts/morning_brief.py
```

## 트러블슈팅

- Ollama 연결 오류:
  - `brew services start ollama`
  - `ollama list`
- 모듈 오류:
  - `source .venv/bin/activate`
  - `pip install -r requirements.txt`
- 음성 입력 안됨:
  - macOS 마이크 권한 허용 확인
# Jarvis
