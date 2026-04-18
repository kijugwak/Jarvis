# Jarvis Local v1

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

## 가장 편한 운영 방식

개발/테스트할 때는 아래 순서가 가장 편합니다.

1. 터미널 1개: `cd /Users/gwaggiju/3_Javis && source .venv/bin/activate`
2. 텍스트 모드 먼저 검증: `python -m app.main`
3. 기능 확인 후 음성 모드: `python -m app.voice_main`
4. 지식 추가 시 `data/knowledge` 파일만 수정하고 바로 재질문

## RAG 지식 문서 넣기

`data/knowledge` 폴더에 `.md` 또는 `.txt` 파일을 넣으면, 질문 시 관련 문맥이 자동으로 검색되어 답변에 반영됩니다.

예시 파일:
- `/Users/gwaggiju/3_Javis/data/knowledge/profile.md`

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
0 8 * * 1-5 /Users/gwaggiju/3_Javis/.venv/bin/python /Users/gwaggiju/3_Javis/scripts/morning_brief.py
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
