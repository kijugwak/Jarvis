from __future__ import annotations

from .chat import handle_user_text
from .stt import record_audio, transcribe
from .tts import speak, to_speech_text


def _control_intent(text: str) -> str:
    t = text.strip().lower().replace(" ", "")
    if t in {"취소", "캔슬"}:
        return "cancel"
    if t in {"종료", "그만", "중지", "꺼", "꺼줘", "끝"}:
        return "shutdown"
    return "none"


def run_voice_once(seconds: int | None = None) -> str:
    audio = record_audio(seconds=seconds)
    user_text = transcribe(audio)
    if not user_text:
        print("You> (인식 실패)")
        return "no_input"
    print(f"You> {user_text}")

    intent = _control_intent(user_text)
    if intent == "cancel":
        msg = "요청을 취소하고 다시 대기할게요."
        print(f"Jarvis> {msg}")
        speak(msg)
        return "cancelled"
    if intent == "shutdown":
        msg = "Jarvis를 종료합니다."
        print(f"Jarvis> {msg}")
        speak(msg)
        return "shutdown"

    answer = handle_user_text(user_text)
    print(f"Jarvis> {answer}")
    speak(to_speech_text(answer))
    return "answered"


def run_voice_loop() -> None:
    print("Jarvis Voice 모드. Ctrl+C 로 종료.")
    while True:
        try:
            result = run_voice_once()
            if result == "shutdown":
                print("Jarvis> 음성 모드를 종료합니다.")
                break
        except KeyboardInterrupt:
            print("\nJarvis> 음성 모드를 종료합니다.")
            break
        except Exception as exc:
            print(f"Jarvis> 오류가 발생했어요: {exc}")


if __name__ == "__main__":
    run_voice_loop()
