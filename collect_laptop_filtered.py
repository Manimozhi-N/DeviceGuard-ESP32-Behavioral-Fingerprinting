import serial
import csv
import time
import re

PORT = "COM16"
BAUD = 115200

OUTPUT_FILE = "laptop_filtered_session.csv"

print("======================================")
print("LAPTOP FILTERED DATA COLLECTION")
print("======================================")

ser = serial.Serial(
    PORT,
    BAUD,
    timeout=1
)

time.sleep(2)

print("ESP32 connected!")
print("Collecting laptop-specific data...")
print("Keep your laptop connected to Tenda.")
print()

rows = []

start_time = time.time()

# Collect for 60 seconds
while time.time() - start_time < 60:

    line = ser.readline().decode(
        "utf-8",
        errors="ignore"
    ).strip()

    if not line:
        continue

    # Match:
    # Laptop Frames/sec: 15 | Size: 30 | IAT(us): 127685 | RSSI: -32

    pattern = (
        r"Laptop Frames/sec:\s*(\d+)"
        r"\s*\|\s*Size:\s*(\d+)"
        r"\s*\|\s*IAT\(us\):\s*(\d+)"
        r"\s*\|\s*RSSI:\s*(-?\d+)"
    )

    match = re.search(pattern, line)

    if not match:
        continue

    frequency = int(match.group(1))
    packet_size = int(match.group(2))
    iat_us = int(match.group(3))
    rssi = int(match.group(4))

    # Ignore seconds where no new laptop frame was detected
    if frequency > 0 and packet_size > 0 and iat_us > 0:

        rows.append([
            packet_size,
            iat_us,
            frequency,
            rssi,
            "Laptop"
        ])

        print(
            packet_size,
            iat_us,
            frequency,
            rssi,
            "Laptop"
        )

ser.close()

# Save CSV
with open(
    OUTPUT_FILE,
    "w",
    newline=""
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "packet_size",
        "iat_us",
        "packet_frequency",
        "rssi",
        "device"
    ])

    writer.writerows(rows)

print()
print("======================================")
print("DATA COLLECTION COMPLETED!")
print("======================================")
print("Samples collected:", len(rows))
print("Saved as:", OUTPUT_FILE)