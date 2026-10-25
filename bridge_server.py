
from flask import Flask, jsonify, send_from_directory
from pathlib import Path
import csv

BASE_DIR = Path(__file__).resolve().parent

# Your website is inside results_graphs/web_dashboard
WEB_DIR = BASE_DIR / "results_graphs" / "web_dashboard"

# Existing machine-learning prediction log
DETECTIONS_FILE = BASE_DIR / "detections.csv"

# Diagnostic frames captured from the ESP32
LIVE_FRAMES_FILE = BASE_DIR / "live_frames.csv"

app = Flask(__name__)


@app.route("/")
def home():
    return send_from_directory(str(WEB_DIR), "index.html")


@app.route("/<path:filename>")
def website_files(filename):
    return send_from_directory(str(WEB_DIR), filename)


def read_csv_records(file_path, limit=500):
    """Read the latest records from a CSV file."""
    if not file_path.exists():
        return []

    with file_path.open(
        "r", newline="", encoding="utf-8-sig"
    ) as file:
        records = list(csv.DictReader(file))

    return records[-limit:]


@app.route("/api/detections")
def detections():
    try:
        return jsonify(read_csv_records(DETECTIONS_FILE))
    except (OSError, csv.Error) as error:
        return jsonify({"error": str(error)}), 500


@app.route("/api/live-frames")
def live_frames():
    try:
        return jsonify(read_csv_records(LIVE_FRAMES_FILE, limit=30))
    except (OSError, csv.Error) as error:
        return jsonify({"error": str(error)}), 500


@app.route("/api/health")
def health():
    return jsonify({
        "server": "running",
        "website_found": (WEB_DIR / "index.html").exists(),
        "detections_csv_found": DETECTIONS_FILE.exists(),
        "live_frames_csv_found": LIVE_FRAMES_FILE.exists()
    })


if __name__ == "__main__":
    print("====================================")
    print(" DeviceGuard Flask Server")
    print("====================================")
    print("Website folder:", WEB_DIR)
    print("index.html exists:", (WEB_DIR / "index.html").exists())
    print("Detections CSV:", DETECTIONS_FILE)
    print("Live frames CSV:", LIVE_FRAMES_FILE)
    print("Open: http://127.0.0.1:5000/")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
