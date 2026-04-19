from __future__ import annotations

import time
import subprocess
import numpy as np
from collections import deque
from pathlib import Path

from .config import config
from .stt import get_model, record_audio, transcribe
from .tts import speak
from .voice_id import VoiceVerifier
from .voice_main import run_voice_once


WAKE_WORDS = ("자비스", "jarvis")
WAKE_SUBSTRINGS = ("자비스", "자비스야", "jarvis")


def _is_wake_word(text: str) -> bool:
    lowered = text.lower().replace(" ", "")
    if any(word in lowered for word in WAKE_WORDS):
        return True
    return any(part in lowered for part in WAKE_SUBSTRINGS)


def _detect_claps(audio: np.ndarray) -> int:
    abs_audio = np.abs(audio)
    # Adaptive threshold: keep baseline low-noise environments stable.
    noise_floor = float(np.percentile(abs_audio, 70))
    threshold = max(config.clap_threshold, noise_floor * 6.0)
    min_gap_samples = int(config.sample_rate * (config.clap_min_gap_ms / 1000.0))
    peaks = np.flatnonzero(abs_audio >= threshold)
    if peaks.size == 0:
        if config.clap_debug:
            print(f"[clap] none threshold={threshold:.3f} noise={noise_floor:.3f}")
        return 0

    clap_count = 1
    last_peak = int(peaks[0])
    for idx in peaks[1:]:
        if int(idx) - last_peak >= min_gap_samples:
            clap_count += 1
            last_peak = int(idx)
    if config.clap_debug:
        print(f"[clap] detected={clap_count} threshold={threshold:.3f} noise={noise_floor:.3f}")
    return clap_count


def run_wake_daemon() -> None:
    print("Jarvis Wake Daemon 시작. Ctrl+C 로 종료.", flush=True)
    print("대기 중... (호출어: 자비스 / jarvis 또는 박수 2번)", flush=True)
    try:
        get_model()
        print("[STT] 모델 워밍업 완료", flush=True)
    except Exception as exc:
        print(f"[STT] 모델 워밍업 실패: {exc}", flush=True)
    clap_times: deque[float] = deque()
    clap_window = config.clap_window_seconds
    verifier: VoiceVerifier | None = None
    last_terminal_open = 0.0
    first_activation_spoken = False
    if config.voice_auth_enabled:
        try:
            verifier = VoiceVerifier.load(
                profile_path=config.voice_profile_path,
                threshold=config.voice_auth_threshold,
                sample_rate=config.sample_rate,
            )
            print(f"[voice-auth] enabled threshold={config.voice_auth_threshold:.2f}", flush=True)
        except Exception as exc:
            print(f"[voice-auth] profile load 실패: {exc}", flush=True)
            verifier = None

    while True:
        try:
            audio = record_audio(seconds=config.wake_listen_seconds)
            detected = _detect_claps(audio)
            now = time.monotonic()
            if detected > 0:
                for _ in range(detected):
                    clap_times.append(now)
            while clap_times and now - clap_times[0] > clap_window:
                clap_times.popleft()

            if len(clap_times) >= config.clap_required_count:
                clap_times.clear()
                if verifier is not None:
                    ok, score = verifier.verify(audio)
                    print(f"[voice-auth:clap] score={score:.3f}", flush=True)
                    if not ok:
                        print("[voice-auth:clap] 등록된 사용자 음성과 불일치", flush=True)
                        continue
                now = time.monotonic()
                if config.show_terminal_on_wake and (now - last_terminal_open) >= config.wake_terminal_cooldown_sec:
                    _show_activation_terminal()
                    last_terminal_open = now
                _play_activation_sound()
                if not first_activation_spoken:
                    greeting = "Did you call me, Master?"
                    first_activation_spoken = True
                else:
                    greeting = "네, 부르셨어요. 말씀하세요."
                print(f"Jarvis> {greeting}", flush=True)
                speak(greeting)
                result = run_voice_once(seconds=config.command_listen_seconds)
                if result == "shutdown":
                    print("Jarvis> Wake Daemon을 종료합니다.", flush=True)
                    break
                print("Jarvis> 다시 대기합니다.", flush=True)
                continue

            heard = transcribe(audio)
            if not heard:
                continue
            print(f"[wake] {heard}", flush=True)
            if not _is_wake_word(heard):
                continue

            if verifier is not None:
                ok, score = verifier.verify(audio)
                print(f"[voice-auth] score={score:.3f}", flush=True)
                if not ok:
                    print("[voice-auth] 등록된 사용자 음성과 불일치", flush=True)
                    continue

            now = time.monotonic()
            if config.show_terminal_on_wake and (now - last_terminal_open) >= config.wake_terminal_cooldown_sec:
                _show_activation_terminal()
                last_terminal_open = now
            _play_activation_sound()
            if not first_activation_spoken:
                greeting = "Did you call me, Master?"
                first_activation_spoken = True
            else:
                greeting = "네, 부르셨어요. 말씀하세요."
            print(f"Jarvis> {greeting}", flush=True)
            speak(greeting)
            result = run_voice_once(seconds=config.command_listen_seconds)
            if result == "shutdown":
                print("Jarvis> Wake Daemon을 종료합니다.", flush=True)
                break
            print("Jarvis> 다시 대기합니다.", flush=True)
        except KeyboardInterrupt:
            print("\nJarvis> Wake Daemon 종료.", flush=True)
            break
        except Exception as exc:
            print(f"Jarvis> Wake Daemon 오류: {exc}", flush=True)
            time.sleep(1.0)


def _show_activation_terminal() -> None:
    script_path = "/Users/gwaggiju/Jarvis/scripts/activation_terminal.sh"
    cmd = f"bash {script_path}"
    script = (
        'tell application "Terminal"\n'
        "  activate\n"
        f'  do script "{cmd}"\n'
        "end tell"
    )
    try:
        subprocess.run(["osascript", "-e", script], check=False)
    except Exception:
        pass


def _play_activation_sound() -> None:
    if not config.activation_sound_enabled:
        return
    sound_path = Path(config.activation_sound_file)
    if not sound_path.exists():
        return
    try:
        subprocess.Popen(["afplay", str(sound_path)])
    except Exception:
        pass


if __name__ == "__main__":
    run_wake_daemon()
