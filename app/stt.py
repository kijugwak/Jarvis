from __future__ import annotations

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

from .config import config

_model: WhisperModel | None = None


def get_model() -> WhisperModel:
    global _model
    if _model is None:
        _model = WhisperModel(config.whisper_model_size, device="cpu", compute_type="int8")
    return _model


def record_audio(seconds: int | None = None) -> np.ndarray:
    duration = seconds if seconds is not None else config.record_seconds
    print(f"[STT] 녹음 시작 ({duration}초)")
    audio = sd.rec(
        int(duration * config.sample_rate),
        samplerate=config.sample_rate,
        channels=1,
        dtype="float32",
    )
    sd.wait()
    print("[STT] 녹음 종료")
    return audio.flatten()


def transcribe(audio: np.ndarray) -> str:
    model = get_model()
    segments, _ = model.transcribe(audio, language="ko")
    text = "".join(seg.text for seg in segments).strip()
    return text
