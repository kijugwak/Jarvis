from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.automation import build_morning_brief


def main() -> None:
    print(build_morning_brief())


if __name__ == "__main__":
    main()
