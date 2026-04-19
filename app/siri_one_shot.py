from __future__ import annotations

import sys

from .chat import handle_user_text
from .tts import speak, to_speech_text


def run_one_shot(user_text: str) -> int:
    text = user_text.strip()
    if not text:
        print("질문이 비어 있어요.")
        return 1
    answer = handle_user_text(text)
    print(answer)
    speak(to_speech_text(answer))
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python -m app.siri_one_shot '<question>'")
        return 1
    return run_one_shot(" ".join(sys.argv[1:]))


if __name__ == "__main__":
    raise SystemExit(main())
