from __future__ import annotations

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

from .config import config

_model: WhisperModel | None = None


def _resolve_input_device() -> int | None:
    # Allow explicit device pinning via env, e.g. AUDIO_INPUT_DEVICE="MacBook Pro Microphone"
    if config.audio_input_device:
        wanted = config.audio_input_device.lower()
        try:
            devices = sd.query_devices()
            for idx, dev in enumerate(devices):
                name = str(dev.get("name", "")).lower()
                if wanted in name and int(dev.get("max_input_channels", 0)) > 0:
                    return idx
        except Exception:
            pass

    try:
        default_in, _ = sd.default.device
        if isinstance(default_in, int) and default_in >= 0:
            return default_in
    except Exception:
        pass

    try:
        devices = sd.query_devices()
    except Exception:
        return None

    for idx, dev in enumerate(devices):
        if int(dev.get("max_input_channels", 0)) > 0:
            return idx
    return None


def get_model() -> WhisperModel:
    global _model
    if _model is None:
        _model = WhisperModel(config.whisper_model_size, device="cpu", compute_type="int8")
    return _model


def record_audio(seconds: int | None = None) -> np.ndarray:
    duration = seconds if seconds is not None else config.record_seconds
    if config.stt_verbose:
        print(f"[STT] 녹음 시작 ({duration}초)", flush=True)
    input_device = _resolve_input_device()
    if input_device is None:
        raise RuntimeError("사용 가능한 입력 마이크를 찾지 못했어요.")
    audio = sd.rec(
        int(duration * config.sample_rate),
        samplerate=config.sample_rate,
        channels=1,
        dtype="float32",
        device=input_device,
    )
    sd.wait()
    if config.stt_verbose:
        print("[STT] 녹음 종료", flush=True)
    return audio.flatten()


def transcribe(audio: np.ndarray) -> str:
    model = get_model()
    segments, _ = model.transcribe(audio, language="ko")
    text = "".join(seg.text for seg in segments).strip()
    return text
