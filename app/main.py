from __future__ import annotations

from .chat import handle_user_text


def run_cli() -> None:
    print("Jarvis CLI 시작. 종료: quit")
    while True:
        user = input("You> ").strip()
        if user.lower() in {"quit", "exit"}:
            print("Jarvis> 다음에 또 봐요.")
            break
        if not user:
            continue
        try:
            answer = handle_user_text(user)
            print(f"Jarvis> {answer}")
        except Exception as exc:
            print(f"Jarvis> 오류가 발생했어요: {exc}")


if __name__ == "__main__":
    run_cli()
