
import pandas as pd
import matplotlib.pyplot as plt
import os

# ==========================================
# SETTINGS
# ==========================================

CSV_FILE = "detections.csv"
OUTPUT_FOLDER = "results_graphs"

# ==========================================
# LOAD DATA
# ==========================================

if not os.path.exists(CSV_FILE):
    print("Error: detections.csv not found!")
    raise SystemExit

df = pd.read_csv(CSV_FILE)

if df.empty:
    print("No detection records found. Run the dashboard first.")
    raise SystemExit

required_columns = [
    "timestamp",
    "packet_size",
    "iat_ms",
    "frequency",
    "confidence"
]

missing = [col for col in required_columns if col not in df.columns]

if missing:
    print("Missing columns:", missing)
    raise SystemExit

df["timestamp"] = pd.to_datetime(
    df["timestamp"], errors="coerce"
)

for col in required_columns[1:]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=required_columns)

if df.empty:
    print("No valid numeric records found.")
    raise SystemExit

df = df.reset_index(drop=True)

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Use record number for a readable sequence of measurements
df["record_number"] = range(1, len(df) + 1)

# ==========================================
# GRAPH 1: PACKET SIZE
# ==========================================

plt.figure(figsize=(10, 5))
plt.plot(df["record_number"], df["packet_size"], marker=".")
plt.title("Wi-Fi Frame Size Over Time")
plt.xlabel("Record Number")
plt.ylabel("Frame Size (bytes)")
plt.grid(True)
plt.tight_layout()
plt.savefig(
    os.path.join(OUTPUT_FOLDER, "packet_size.png")
)
plt.close()

# ==========================================
# GRAPH 2: INTER-ARRIVAL TIME
# ==========================================

plt.figure(figsize=(10, 5))
plt.plot(df["record_number"], df["iat_ms"], marker=".")
plt.title("Inter-Arrival Time (IAT) Over Time")
plt.xlabel("Record Number")
plt.ylabel("IAT (milliseconds)")
plt.grid(True)
plt.tight_layout()
plt.savefig(
    os.path.join(OUTPUT_FOLDER, "iat.png")
)
plt.close()

# ==========================================
# GRAPH 3: FRAME FREQUENCY
# ==========================================

plt.figure(figsize=(10, 5))
plt.plot(df["record_number"], df["frequency"], marker=".")
plt.title("Wi-Fi Frame Frequency Over Time")
plt.xlabel("Record Number")
plt.ylabel("Frames per Second")
plt.grid(True)
plt.tight_layout()
plt.savefig(
    os.path.join(OUTPUT_FOLDER, "frequency.png")
)
plt.close()

# ==========================================
# GRAPH 4: MODEL CONFIDENCE
# ==========================================

plt.figure(figsize=(10, 5))
plt.plot(df["record_number"], df["confidence"], marker=".")
plt.axhline(
    y=70,
    linestyle="--",
    label="70% confidence threshold"
)
plt.title("Model Confidence Over Time")
plt.xlabel("Record Number")
plt.ylabel("Confidence (%)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(
    os.path.join(OUTPUT_FOLDER, "confidence.png")
)
plt.close()

# ==========================================
# SUMMARY
# ==========================================

print("\n========== DETECTION SUMMARY ==========")
print("Total records:", len(df))
print("Most frequent prediction:")
print(df["device"].value_counts().to_string())
print("\nAverage packet size:",
      round(df["packet_size"].mean(), 2), "bytes")
print("Average IAT:",
      round(df["iat_ms"].mean(), 2), "ms")
print("Average frequency:",
      round(df["frequency"].mean(), 2), "frames/sec")
print("Average model confidence:",
      round(df["confidence"].mean(), 2), "%")

print("\nGraphs saved in:", OUTPUT_FOLDER)
print("=======================================")
