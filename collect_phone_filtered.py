import serial
import csv
import re
import time

PORT = "COM16"
BAUD = 115200

OUTPUT_FILE = "phone_filtered_session.csv"

ser = serial.Serial(PORT, BAUD, timeout=1)

time.sleep(2)

print("======================================")
print("PHONE FILTERED DATA COLLECTION")
print("======================================")
print("ESP32 connected!")
print("Collecting phone-specific data...")
print("Keep your phone connected to Tenda.")
print()

pattern = re.compile(
    r"Phone Frames/sec:\s*(\d+)\s*\|\s*Size:\s*(\d+)\s*\|\s*IAT\(us\):\s*(\d+)\s*\|\s*RSSI:\s*(-?\d+)"
)

rows = []

start_time = time.time()

# Collect for 60 seconds
while time.time() - start_time < 60:

    line = ser.readline().decode(
        "utf-8",
        errors="ignore"
    ).strip()

    match = pattern.search(line)

    if not match:
        continue

    frequency = int(match.group(1))
    packet_size = int(match.group(2))
    iat_us = int(match.group(3))
    rssi = int(match.group(4))

    # Only save NEW phone observations
    if frequency > 0 and packet_size > 0 and iat_us > 0:

        rows.append([
            packet_size,
            iat_us,
            frequency,
            rssi,
            "Phone"
        ])

        print(
            packet_size,
            iat_us,
            frequency,
            rssi,
            "Phone"
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