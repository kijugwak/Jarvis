from __future__ import annotations

from .brain import ask_jarvis
from .stt import record_audio, transcribe
from .tts import speak


def run_voice_once(seconds: int | None = None) -> bool:
    audio = record_audio(seconds=seconds)
    user_text = transcribe(audio)
    if not user_text:
        print("You> (인식 실패)")
        return False
    print(f"You> {user_text}")
    answer = ask_jarvis(user_text)
    print(f"Jarvis> {answer}")
    speak(answer)
    return True


def run_voice_loop() -> None:
    print("Jarvis Voice 모드. Ctrl+C 로 종료.")
    while True:
        try:
            run_voice_once()
        except KeyboardInterrupt:
            print("\nJarvis> 음성 모드를 종료합니다.")
            break
        except Exception as exc:
            print(f"Jarvis> 오류가 발생했어요: {exc}")


if __name__ == "__main__":
    run_voice_loop()
