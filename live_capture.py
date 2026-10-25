
import serial
import re
import csv
import time
from pathlib import Path
from datetime import datetime

PORT = "COM16"
BAUD = 115200

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "live_frames.csv"

pattern = re.compile(
    r"Frames/sec:\s*(\d+)"
    r"\s*\|\s*Type:\s*(DATA|MGMT)"
    r"\s*\|\s*ToDS:\s*(\d+)"
    r"\s*\|\s*FromDS:\s*(\d+)"
    r"\s*\|\s*A1:\s*([0-9A-Fa-f:]+)"
    r"\s*\|\s*A2:\s*([0-9A-Fa-f:]+)"
    r"\s*\|\s*A3:\s*([0-9A-Fa-f:]+)"
    r"(?:\s*\|\s*A4:\s*([0-9A-Fa-f:]+))?"
    r"\s*\|\s*Size:\s*(\d+)"
    r"\s*\|\s*RSSI:\s*(-?\d+)",
    re.IGNORECASE
)

try:
    with LOG_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp", "reported_frames_per_sec", "frame_type",
            "to_ds", "from_ds", "a1", "a2", "a3", "a4",
            "packet_size", "rssi"
        ])

    print("Connecting to ESP32 on", PORT)

    with serial.Serial(PORT, BAUD, timeout=2) as ser:
        time.sleep(2)
        print("ESP32 connected. Capturing diagnostic frames.")
        print("Saved to:", LOG_FILE)
        print("Press Ctrl+C to stop.")

        with LOG_FILE.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            while True:
                line = ser.readline().decode(
                    "utf-8", errors="ignore"
                ).strip()

                match = pattern.search(line)
                if not match:
                    continue

                groups = match.groups()
                record = [
                    datetime.now().isoformat(timespec="seconds"),
                    groups[0], groups[1], groups[2], groups[3],
                    groups[4], groups[5], groups[6], groups[7] or "",
                    groups[8], groups[9]
                ]

                writer.writerow(record)
                f.flush()

                print(
                    f"Captured {groups[1]} frame | "
                    f"Size={groups[8]} bytes | RSSI={groups[9]} dBm"
                )

except KeyboardInterrupt:
    print("\nCapture stopped. CSV saved.")

except serial.SerialException as e:
    print("Serial connection error:", e)
    print("Close Arduino Serial Monitor and other serial scripts.")
