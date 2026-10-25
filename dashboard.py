
import tkinter as tk
import serial
import joblib
import re
import pandas as pd
import threading
import time
import csv
import os
from datetime import datetime

# ==========================================
# SETTINGS
# ==========================================

PORT = "COM16"
BAUD = 115200
MODEL_FILE = "final_filtered_model.pkl"
LOG_FILE = "detections.csv"

CONFIDENCE_THRESHOLD = 70

# ==========================================
# LOAD MODEL
# ==========================================

try:
    model = joblib.load(MODEL_FILE)
except Exception as e:
    raise SystemExit(
        f"Could not load {MODEL_FILE}: {e}\n"
        "Check that the model file is in the project folder."
    )

# ==========================================
# CREATE CSV LOG FILE
# ==========================================

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "timestamp",
            "device",
            "packet_size",
            "iat_ms",
            "frequency",
            "rssi",
            "confidence",
            "status"
        ])

# ==========================================
# SERIAL CONNECTION
# ==========================================

ser = None

try:
    ser = serial.Serial(
        PORT,
        BAUD,
        timeout=1
    )
    time.sleep(2)
    print(f"ESP32 connected successfully on {PORT}")

except Exception as e:
    print("Serial connection error:", e)
    print("Close Arduino Serial Monitor and check the COM port.")

# ==========================================
# MAIN WINDOW
# ==========================================

root = tk.Tk()
root.title("ESP32 Behavioral Device Fingerprinting")
root.geometry("1000x650")
root.configure(bg="#111827")

# ==========================================
# TITLE
# ==========================================

title = tk.Label(
    root,
    text="ESP32 BEHAVIORAL DEVICE FINGERPRINTING",
    font=("Arial", 22, "bold"),
    fg="white",
    bg="#111827"
)
title.pack(pady=20)

subtitle = tk.Label(
    root,
    text="Real-Time Wi-Fi Device Detection",
    font=("Arial", 12),
    fg="#9CA3AF",
    bg="#111827"
)
subtitle.pack()

# ==========================================
# DEVICE RESULT
# ==========================================

device_label = tk.Label(
    root,
    text="WAITING...",
    font=("Arial", 30, "bold"),
    fg="#60A5FA",
    bg="#111827"
)
device_label.pack(pady=25)

status_label = tk.Label(
    root,
    text="Waiting for ESP32 data...",
    font=("Arial", 15, "bold"),
    fg="#FBBF24",
    bg="#111827"
)
status_label.pack()

# ==========================================
# DATA FRAME
# ==========================================

data_frame = tk.Frame(
    root,
    bg="#1F2937"
)
data_frame.pack(
    pady=25,
    padx=35,
    fill="x"
)

# ==========================================
# DATA LABELS
# ==========================================

packet_value = tk.Label(
    data_frame,
    text="--",
    font=("Arial", 20, "bold"),
    fg="white",
    bg="#1F2937"
)
packet_value.grid(row=0, column=0, padx=35, pady=20)

iat_value = tk.Label(
    data_frame,
    text="--",
    font=("Arial", 20, "bold"),
    fg="white",
    bg="#1F2937"
)
iat_value.grid(row=0, column=1, padx=35, pady=20)

frequency_value = tk.Label(
    data_frame,
    text="--",
    font=("Arial", 20, "bold"),
    fg="white",
    bg="#1F2937"
)
frequency_value.grid(row=0, column=2, padx=35, pady=20)

rssi_value = tk.Label(
    data_frame,
    text="--",
    font=("Arial", 20, "bold"),
    fg="white",
    bg="#1F2937"
)
rssi_value.grid(row=0, column=3, padx=35, pady=20)

# ==========================================
# HEADINGS
# ==========================================

tk.Label(
    data_frame,
    text="PACKET SIZE",
    font=("Arial", 10, "bold"),
    fg="#9CA3AF",
    bg="#1F2937"
).grid(row=1, column=0)

tk.Label(
    data_frame,
    text="IAT",
    font=("Arial", 10, "bold"),
    fg="#9CA3AF",
    bg="#1F2937"
).grid(row=1, column=1)

tk.Label(
    data_frame,
    text="FREQUENCY",
    font=("Arial", 10, "bold"),
    fg="#9CA3AF",
    bg="#1F2937"
).grid(row=1, column=2)

tk.Label(
    data_frame,
    text="RSSI",
    font=("Arial", 10, "bold"),
    fg="#9CA3AF",
    bg="#1F2937"
).grid(row=1, column=3)

# ==========================================
# CONFIDENCE
# ==========================================

confidence_label = tk.Label(
    root,
    text="Confidence: --",
    font=("Arial", 16, "bold"),
    fg="white",
    bg="#111827"
)
confidence_label.pack(pady=20)

# ==========================================
# CSV LOGGING FUNCTION
# ==========================================

def log_detection(
    prediction,
    packet_size,
    iat_ms,
    frequency,
    rssi,
    confidence,
    status
):
    try:
        with open(
            LOG_FILE,
            "a",
            newline="",
            encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.now().isoformat(timespec="seconds"),
                prediction,
                packet_size,
                round(iat_ms, 2),
                frequency,
                rssi,
                round(confidence, 2),
                status
            ])

    except OSError as e:
        print("CSV logging error:", e)

# ==========================================
# SERIAL DATA PARSER
# Expected ESP32 line:
# Phone|Laptop Frames/sec: 4 | Size: 30 |
# IAT(us): 307650 | RSSI: -86
# ==========================================

pattern = re.compile(
    r"(?:Phone|Laptop)\s+Frames/sec:\s*(\d+)"
    r"\s*\|\s*Size:\s*(\d+)"
    r"\s*\|\s*IAT\(us\):\s*(\d+)"
    r"\s*\|\s*RSSI:\s*(-?\d+)",
    re.IGNORECASE
)

# ==========================================
# READ ESP32 SERIAL DATA
# ==========================================

def read_serial():
    while ser is not None:
        try:
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

            if frequency <= 0:
                continue

            iat_ms = iat_us / 1000.0

            data = pd.DataFrame(
                [[packet_size, iat_us, frequency, rssi]],
                columns=[
                    "packet_size",
                    "iat_us",
                    "packet_frequency",
                    "rssi"
                ]
            )

            prediction = model.predict(data)[0]
            probabilities = model.predict_proba(data)[0]
            confidence = float(max(probabilities) * 100)

            # A model prediction is not proof of authorization.
            if confidence >= CONFIDENCE_THRESHOLD:
                status = "MODEL CONFIDENT"
            else:
                status = "LOW CONFIDENCE"

            # Update the GUI and write CSV from the GUI thread.
            root.after(
                0,
                update_dashboard,
                prediction,
                packet_size,
                iat_ms,
                frequency,
                rssi,
                confidence,
                status
            )

        except (serial.SerialException, OSError) as e:
            print("Serial read error:", e)
            break

        except Exception as e:
            print("Prediction error:", e)

# ==========================================
# UPDATE DASHBOARD AND LOG PREDICTION
# ==========================================

def update_dashboard(
    prediction,
    packet_size,
    iat_ms,
    frequency,
    rssi,
    confidence,
    status
):
    if not root.winfo_exists():
        return

    device_label.config(text=str(prediction).upper())

    packet_value.config(text=f"{packet_size} B")
    iat_value.config(text=f"{iat_ms:.2f} ms")
    frequency_value.config(text=f"{frequency}/sec")
    rssi_value.config(text=f"{rssi} dBm")

    confidence_label.config(
        text=f"Confidence: {confidence:.1f}%"
    )

    if status == "MODEL CONFIDENT":
        status_label.config(
            text="MODEL CONFIDENT - IDENTITY UNVERIFIED",
            fg="#34D399"
        )
    else:
        status_label.config(
            text="LOW CONFIDENCE - CHECK DEVICE",
            fg="#F87171"
        )

    log_detection(
        prediction,
        packet_size,
        iat_ms,
        frequency,
        rssi,
        confidence,
        status
    )

# ==========================================
# CLOSE APPLICATION SAFELY
# ==========================================

def close_dashboard():
    global ser

    try:
        if ser is not None and ser.is_open:
            ser.close()
    except Exception:
        pass

    root.destroy()

root.protocol("WM_DELETE_WINDOW", close_dashboard)

# ==========================================
# START SERIAL THREAD
# ==========================================

if ser is not None:
    thread = threading.Thread(
        target=read_serial,
        daemon=True
    )
    thread.start()
else:
    status_label.config(
        text="ESP32 NOT CONNECTED - CHECK COM16",
        fg="#F87171"
    )

# ==========================================
# START GUI
# ==========================================

root.mainloop()
