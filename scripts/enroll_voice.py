from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import config
from app.stt import record_audio
from app.voice_id import extract_voice_embedding, save_profile


def main() -> None:
    print("[voice-enroll] 등록을 시작합니다.")
    print("[voice-enroll] 5초 동안 평소처럼 '자비스'를 여러 번 말해 주세요.")
    audio = record_audio(seconds=5)
    emb = extract_voice_embedding(audio, sample_rate=config.sample_rate)
    save_profile(config.voice_profile_path, emb)
    print(f"[voice-enroll] 완료: {config.voice_profile_path}")


if __name__ == "__main__":
    main()
