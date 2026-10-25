import serial
import time

ser = serial.Serial("COM16", 115200, timeout=1)

print("ESP32 connected!")
print("Reading data for 20 seconds...")
print()

start = time.time()

while time.time() - start < 20:

    line = ser.readline().decode(
        "utf-8",
        errors="ignore"
    ).strip()

    if line:
        print(line)

ser.close()

print()
print("TEST COMPLETED")