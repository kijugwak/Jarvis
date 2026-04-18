from dataclasses import dataclass
import os
from pathlib import Path


@dataclass
class Config:
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")
    ollama_keep_alive: str = os.getenv("OLLAMA_KEEP_ALIVE", "30m")
    ollama_num_predict: int = int(os.getenv("OLLAMA_NUM_PREDICT", "120"))
    whisper_model_size: str = os.getenv("WHISPER_MODEL_SIZE", "base")
    sample_rate: int = int(os.getenv("AUDIO_SAMPLE_RATE", "16000"))
    record_seconds: int = int(os.getenv("RECORD_SECONDS", "5"))
    wake_listen_seconds: int = int(os.getenv("WAKE_LISTEN_SECONDS", "2"))
    command_listen_seconds: int = int(os.getenv("COMMAND_LISTEN_SECONDS", "6"))
    knowledge_dir: str = os.getenv("KNOWLEDGE_DIR", str(Path.cwd() / "data" / "knowledge"))
    knowledge_extensions: tuple[str, ...] = (".txt", ".md")
    rag_top_k: int = int(os.getenv("RAG_TOP_K", "3"))
    rag_chunk_size: int = int(os.getenv("RAG_CHUNK_SIZE", "700"))
    rag_chunk_overlap: int = int(os.getenv("RAG_CHUNK_OVERLAP", "120"))


config = Config()
