from dataclasses import dataclass
import os
from pathlib import Path


@dataclass
class Config:
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")
    ollama_keep_alive: str = os.getenv("OLLAMA_KEEP_ALIVE", "30m")
    ollama_num_predict: int = int(os.getenv("OLLAMA_NUM_PREDICT", "80"))
    whisper_model_size: str = os.getenv("WHISPER_MODEL_SIZE", "base")
    sample_rate: int = int(os.getenv("AUDIO_SAMPLE_RATE", "16000"))
    audio_input_device: str = os.getenv("AUDIO_INPUT_DEVICE", "").strip()
    record_seconds: int = int(os.getenv("RECORD_SECONDS", "5"))
    wake_listen_seconds: int = int(os.getenv("WAKE_LISTEN_SECONDS", "3"))
    command_listen_seconds: int = int(os.getenv("COMMAND_LISTEN_SECONDS", "4"))
    clap_threshold: float = float(os.getenv("CLAP_THRESHOLD", "0.18"))
    clap_min_gap_ms: int = int(os.getenv("CLAP_MIN_GAP_MS", "120"))
    clap_required_count: int = int(os.getenv("CLAP_REQUIRED_COUNT", "2"))
    clap_window_seconds: float = float(os.getenv("CLAP_WINDOW_SECONDS", "1.4"))
    clap_debug: bool = os.getenv("CLAP_DEBUG", "0").strip() in {"1", "true", "TRUE", "yes"}
    tts_voice: str = os.getenv("TTS_VOICE", "").strip()
    tts_rate: int = int(os.getenv("TTS_RATE", "165"))
    voice_auth_enabled: bool = os.getenv("VOICE_AUTH_ENABLED", "0").strip() in {"1", "true", "TRUE", "yes"}
    voice_profile_path: str = os.getenv("VOICE_PROFILE_PATH", str(Path.cwd() / "data" / "voice" / "owner.npy"))
    voice_auth_threshold: float = float(os.getenv("VOICE_AUTH_THRESHOLD", "0.85"))
    show_terminal_on_wake: bool = os.getenv("SHOW_TERMINAL_ON_WAKE", "1").strip() in {"1", "true", "TRUE", "yes"}
    wake_terminal_cooldown_sec: float = float(os.getenv("WAKE_TERMINAL_COOLDOWN_SEC", "8"))
    activation_sound_enabled: bool = os.getenv("ACTIVATION_SOUND_ENABLED", "1").strip() in {"1", "true", "TRUE", "yes"}
    activation_sound_file: str = os.getenv("ACTIVATION_SOUND_FILE", "/System/Library/Sounds/Glass.aiff").strip()
    activation_banner_text: str = os.getenv("ACTIVATION_BANNER_TEXT", "JARVIS ONLINE").strip()
    stt_verbose: bool = os.getenv("STT_VERBOSE", "0").strip() in {"1", "true", "TRUE", "yes"}
    knowledge_dir: str = os.getenv("KNOWLEDGE_DIR", str(Path.cwd() / "data" / "knowledge"))
    knowledge_extensions: tuple[str, ...] = (".txt", ".md")
    rag_top_k: int = int(os.getenv("RAG_TOP_K", "3"))
    rag_chunk_size: int = int(os.getenv("RAG_CHUNK_SIZE", "700"))
    rag_chunk_overlap: int = int(os.getenv("RAG_CHUNK_OVERLAP", "120"))


config = Config()
