
import serial
import time

PORT = "COM16"
BAUD = 115200

try:
    print("Connecting to ESP32...")

    with serial.Serial(PORT, BAUD, timeout=2) as esp:
        time.sleep(2)
        print("Connected! Reading ESP32 output.")
        print("Press Ctrl+C to stop.\n")

        while True:
            line = esp.readline().decode(
                "utf-8", errors="ignore"
            ).strip()

            if line:
                print(line)

except KeyboardInterrupt:
    print("\nESP32 test stopped.")

except serial.SerialException as error:
    print("Serial connection error:", error)
    print("Check COM16 and close Arduino Serial Monitor.")

