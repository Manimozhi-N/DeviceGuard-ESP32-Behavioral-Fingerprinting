
import pandas as pd
from pathlib import Path

# Separate session files already in your project
files = [
    ("phone_data.csv", "Phone", "Phone Session 1"),
    ("phone_session2.csv", "Phone", "Phone Session 2"),
    ("phone_session3.csv", "Phone", "Phone Session 3"),
    ("laptop_data.csv", "Laptop", "Laptop Session 1"),
    ("laptop_session2.csv", "Laptop", "Laptop Session 2"),
    ("laptop_session3.csv", "Laptop", "Laptop Session 3"),
]

all_sessions = []

print("\n========== SESSION FILE CHECK ==========\n")

for filename, expected_device, session_name in files:
    path = Path(filename)

    if not path.exists():
        print(f"{filename}: FILE NOT FOUND")
        continue

    df = pd.read_csv(path)

    print(f"{session_name}: {filename}")
    print("Rows:", len(df))
    print("Columns:", df.columns.tolist())

    if "device" in df.columns:
        print("Labels:", df["device"].value_counts().to_dict())

    df["session_id"] = session_name
    all_sessions.append(df)
    print("-" * 45)

if not all_sessions:
    print("No session files were found.")
    raise SystemExit

combined = pd.concat(all_sessions, ignore_index=True)

print("\nCombined rows:", len(combined))
print("\nRows by session:")
print(combined["session_id"].value_counts().to_string())

print("\nDevice labels by session:")
if "device" in combined.columns:
    print(pd.crosstab(combined["session_id"], combined["device"]))

# Save a new inspection file; existing files remain unchanged.
combined.to_csv("session_check_combined.csv", index=False)

print("\nSaved inspection copy: session_check_combined.csv")
print("Existing datasets and models were not modified.")
