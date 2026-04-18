from __future__ import annotations

from .brain import ask_jarvis
from .rag import format_context, retrieve_context
from .tools import try_local_tool


def run_cli() -> None:
    print("Jarvis Local CLI 시작. 종료: quit")
    while True:
        user = input("You> ").strip()
        if user.lower() in {"quit", "exit"}:
            print("Jarvis> 다음에 또 봐요.")
            break
        if not user:
            continue
        try:
            tool_result = try_local_tool(user)
            if tool_result.handled:
                print(f"Jarvis> {tool_result.message}")
                continue

            chunks = retrieve_context(user)
            context_text = format_context(chunks)
            answer = ask_jarvis(user, context_text=context_text)
            print(f"Jarvis> {answer}")
        except Exception as exc:
            print(f"Jarvis> 오류가 발생했어요: {exc}")


if __name__ == "__main__":
    run_cli()
