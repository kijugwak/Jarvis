from __future__ import annotations

import subprocess
from threading import Thread

import requests
import rumps

from .config import config
from .voice_main import run_voice_once


def _ensure_ollama() -> None:
    try:
        requests.get(f"{config.ollama_base_url}/api/tags", timeout=2).raise_for_status()
        return
    except Exception:
        pass
    subprocess.run(["brew", "services", "start", "ollama"], check=False)


class JarvisMenuBarApp(rumps.App):
    def __init__(self) -> None:
        super().__init__("Jarvis", menu=["음성 1회 듣기", "종료"])
        self.title = "J"
        self._busy = False

    @rumps.clicked("음성 1회 듣기")
    def listen_once(self, _: rumps.MenuItem) -> None:
        if self._busy:
            rumps.notification("Jarvis", "처리 중", "이전 요청을 처리하고 있어요.")
            return
        self._busy = True
        rumps.notification("Jarvis", "음성 입력", "지금부터 질문을 말씀하세요.")
        Thread(target=self._voice_worker, daemon=True).start()

    def _voice_worker(self) -> None:
        try:
            ok = run_voice_once(seconds=config.command_listen_seconds)
            if ok:
                rumps.notification("Jarvis", "완료", "음성 요청 처리를 마쳤어요.")
            else:
                rumps.notification("Jarvis", "인식 실패", "다시 한 번 말씀해 주세요.")
        except Exception as exc:
            rumps.notification("Jarvis", "오류", str(exc))
        finally:
            self._busy = False

    @rumps.clicked("종료")
    def quit_app(self, _: rumps.MenuItem) -> None:
        rumps.quit_application()


def run_menubar_app() -> None:
    _ensure_ollama()
    rumps.notification("Jarvis", "메뉴바 실행됨", "상단 메뉴바에서 J 아이콘을 눌러 질문하세요.")
    JarvisMenuBarApp().run()


if __name__ == "__main__":
    run_menubar_app()
