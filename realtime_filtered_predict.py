
import serial
import re
import time
from collections import deque

PORT = "COM16"
BAUD = 115200

# Read diagnostic data only; do not make device predictions yet.
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

# Keep recent timestamps for diagnostic measurement only.
recent_times = deque(maxlen=100)

print("======================================")
print(" ESP32 LIVE FRAME DIAGNOSTIC")
print("======================================")
print("Connecting to ESP32 on", PORT)

try:
    with serial.Serial(PORT, BAUD, timeout=2) as ser:
        time.sleep(2)
        print("ESP32 connected!")
        print("Reading frames. Press Ctrl+C to stop.\n")

        while True:
            line = ser.readline().decode(
                "utf-8", errors="ignore"
            ).strip()

            match = pattern.search(line)
            if not match:
                continue

            frequency = int(match.group(1))
            frame_type = match.group(2).upper()
            to_ds = int(match.group(3))
            from_ds = int(match.group(4))
            a1, a2, a3 = match.group(5), match.group(6), match.group(7)
            a4 = match.group(8)
            packet_size = int(match.group(9))
            rssi = int(match.group(10))

            now = time.monotonic()
            recent_times.append(now)

            print("--------------------------------------")
            print(f"Frame rate reported: {frequency}/sec")
            print(f"Type: {frame_type}")
            print(f"ToDS: {to_ds} | FromDS: {from_ds}")
            print(f"A1: {a1} | A2: {a2} | A3: {a3}")
            if a4:
                print(f"A4: {a4}")
            print(f"Frame size: {packet_size} bytes")
            print(f"RSSI: {rssi} dBm")

            if len(recent_times) >= 2:
                iat_ms = (
                    recent_times[-1] - recent_times[-2]
                ) * 1000
                print(f"Time between received lines: {iat_ms:.2f} ms")

            print("Note: No Phone/Laptop identity prediction made.")

except KeyboardInterrupt:
    print("\nStopped.")

except serial.SerialException as error:
    print("Serial connection error:", error)
    print("Close Arduino Serial Monitor and check COM16.")
