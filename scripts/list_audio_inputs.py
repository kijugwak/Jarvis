from __future__ import annotations

import sounddevice as sd


def main() -> None:
    devices = sd.query_devices()
    for idx, dev in enumerate(devices):
        in_ch = int(dev.get("max_input_channels", 0))
        if in_ch > 0:
            print(f"{idx}: {dev.get('name')} (input_channels={in_ch})")


if __name__ == "__main__":
    main()
