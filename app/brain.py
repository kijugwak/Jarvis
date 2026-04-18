from __future__ import annotations

import requests

from .config import config

SYSTEM_PROMPT = """너는 로컬 개인 비서 Jarvis다.
규칙:
1) 짧고 명확하게 답변한다.
2) 삭제/전송/결제/외부 공개 등 위험 작업은 실행 전 재확인 질문을 한다.
3) 모르면 모른다고 말하고, 다음 행동을 제안한다.
"""


def ask_jarvis(user_text: str, context_text: str = "") -> str:
    system_prompt = SYSTEM_PROMPT
    if context_text:
        system_prompt += (
            "\n4) 아래 참고 문맥이 있으면 우선 활용한다.\n"
            "5) 참고 문맥에 없는 사실은 추측하지 말고 모른다고 말한다.\n"
            "\n[참고 문맥]\n"
            f"{context_text}"
        )

    payload = {
        "model": config.ollama_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ],
        "keep_alive": config.ollama_keep_alive,
        "options": {
            "num_predict": config.ollama_num_predict,
            "temperature": 0.2,
        },
        "stream": False,
    }
    response = requests.post(
        f"{config.ollama_base_url}/api/chat",
        json=payload,
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    return data["message"]["content"].strip()
