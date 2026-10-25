import serial
import pandas as pd
import joblib
import time

# ESP32
PORT = "COM16"
BAUD_RATE = 115200

# Load trained model
model = joblib.load("real_device_model.pkl")

print("====================================")
print("REAL-TIME DEVICE FINGERPRINTING")
print("====================================")
print("Connecting to ESP32...")

ser = serial.Serial(PORT, BAUD_RATE, timeout=1)

time.sleep(2)

print("ESP32 connected!")
print("Waiting for Wi-Fi data...")
print()

while True:

    line = ser.readline().decode(
        "utf-8",
        errors="ignore"
    ).strip()

    if not line:
        continue

    # Ignore text messages from ESP32
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

        # Ignore invalid measurements
        if packet_size <= 0 or iat_us <= 0:
            continue

        # Convert microseconds → milliseconds
        iat_ms = iat_us / 1000

        # Create input for ML model
        data = pd.DataFrame(
            [[
                packet_size,
                iat_ms,
                packet_frequency,
                rssi
            ]],
            columns=[
                "packet_size",
                "iat_ms",
                "packet_frequency",
                "rssi"
            ]
        )

        # Prediction
        prediction = model.predict(data)[0]

        print(
            f"Size: {packet_size:4d} | "
            f"IAT: {iat_ms:8.2f} ms | "
            f"Frequency: {packet_frequency:3d} | "
            f"RSSI: {rssi:4d} | "
            f"Prediction: {prediction}"
        )

    except ValueError:
        continue