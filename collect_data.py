import serial
import csv
import time

# ESP32 COM port
PORT = "COM16"
BAUD_RATE = 115200

# Device label
DEVICE_NAME = "Laptop"
# Output CSV file
OUTPUT_FILE = "laptop_session3.csv"

print("Connecting to ESP32...")

ser = serial.Serial(PORT, BAUD_RATE, timeout=1)

# Give serial connection time to start
time.sleep(2)

print("ESP32 connected!")
print("Collecting data for 60 seconds...")
print("Device:", DEVICE_NAME)

with open(OUTPUT_FILE, "w", newline="") as file:

    writer = csv.writer(file)

    # CSV header
    writer.writerow([
        "packet_size",
        "iat_us",
        "packet_frequency",
        "rssi",
        "device"
    ])

    start_time = time.time()

    while time.time() - start_time < 60:

        line = ser.readline().decode(
            "utf-8",
            errors="ignore"
        ).strip()

        if not line:
            continue

        # Ignore ESP32 messages
        if not line[0].isdigit():
            continue

        values = line.split(",")

        if len(values) != 4:
            continue

        try:
            packet_size = int(values[0])
            iat_us = int(values[1])
            packet_frequency = int(values[2])
            rssi = int(values[3])

            writer.writerow([
                packet_size,
                iat_us,
                packet_frequency,
                rssi,
                DEVICE_NAME
            ])

            print(
                packet_size,
                iat_us,
                packet_frequency,
                rssi,
                DEVICE_NAME
            )

        except ValueError:
            continue

ser.close()

print()
print("DATA COLLECTION COMPLETED!")
print("Saved as:", OUTPUT_FILE)