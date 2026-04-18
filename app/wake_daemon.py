from __future__ import annotations

from .config import config
from .stt import record_audio, transcribe
from .voice_main import run_voice_once


WAKE_WORDS = ("자비스", "jarvis")


def _is_wake_word(text: str) -> bool:
    lowered = text.lower()
    return any(word in lowered for word in WAKE_WORDS)


def run_wake_daemon() -> None:
    print("Jarvis Wake Daemon 시작. Ctrl+C 로 종료.")
    print("대기 중... (호출어: 자비스 / jarvis)")
    while True:
        try:
            audio = record_audio(seconds=config.wake_listen_seconds)
            heard = transcribe(audio)
            if not heard:
                continue
            print(f"[wake] {heard}")
            if not _is_wake_word(heard):
                continue

            print("Jarvis> 네, 부르셨어요. 말씀하세요.")
            run_voice_once(seconds=config.command_listen_seconds)
            print("Jarvis> 다시 대기합니다.")
        except KeyboardInterrupt:
            print("\nJarvis> Wake Daemon 종료.")
            break
        except Exception as exc:
            print(f"Jarvis> Wake Daemon 오류: {exc}")


if __name__ == "__main__":
    run_wake_daemon()
