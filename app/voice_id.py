from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.signal import stft


def extract_voice_embedding(audio: np.ndarray, sample_rate: int) -> np.ndarray:
    if audio.size == 0:
        return np.zeros(64, dtype=np.float32)

    # Normalize and compute a compact spectral signature.
    x = audio.astype(np.float32)
    peak = float(np.max(np.abs(x))) if x.size else 0.0
    if peak > 0:
        x = x / peak

    _, _, z = stft(x, fs=sample_rate, nperseg=400, noverlap=240)
    mag = np.abs(z)
    if mag.size == 0:
        return np.zeros(64, dtype=np.float32)

    spec = np.log1p(mag).mean(axis=1)
    # Downsample/resize to fixed dimension.
    src_idx = np.linspace(0, max(len(spec) - 1, 0), num=len(spec))
    dst_idx = np.linspace(0, max(len(spec) - 1, 0), num=64)
    emb = np.interp(dst_idx, src_idx, spec).astype(np.float32)

    norm = float(np.linalg.norm(emb))
    if norm > 0:
        emb /= norm
    return emb


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    an = float(np.linalg.norm(a))
    bn = float(np.linalg.norm(b))
    if an == 0.0 or bn == 0.0:
        return 0.0
    return float(np.dot(a, b) / (an * bn))


@dataclass
class VoiceVerifier:
    profile: np.ndarray
    threshold: float
    sample_rate: int

    @classmethod
    def load(cls, profile_path: str, threshold: float, sample_rate: int) -> "VoiceVerifier":
        arr = np.load(profile_path).astype(np.float32)
        return cls(profile=arr, threshold=threshold, sample_rate=sample_rate)

    def verify(self, audio: np.ndarray) -> tuple[bool, float]:
        emb = extract_voice_embedding(audio, self.sample_rate)
        score = cosine_similarity(self.profile, emb)
        return score >= self.threshold, score


def save_profile(path: str, embedding: np.ndarray) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    np.save(p, embedding.astype(np.float32))
