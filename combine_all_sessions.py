import pandas as pd

files = [
    "phone_data.csv",
    "phone_session2.csv",
    "phone_session3.csv",
    "laptop_data.csv",
    "laptop_session2.csv",
    "laptop_session3.csv"
]

all_data = []

for file in files:
    data = pd.read_csv(file)
    all_data.append(data)

# Combine all sessions
data = pd.concat(all_data, ignore_index=True)

# Remove invalid rows
data = data[
    (data["packet_size"] > 0) &
    (data["iat_us"] > 0) &
    (data["packet_frequency"] > 0) &
    (data["rssi"] != 0)
].copy()

# Convert IAT to milliseconds
data["iat_ms"] = data["iat_us"] / 1000

# Save
data.to_csv("final_6session_dataset.csv", index=False)

print("======================================")
print("FINAL 6-SESSION DATASET")
print("======================================")

print("Total samples:", len(data))

print()
print("Device counts:")
print(data["device"].value_counts())

print()
print("Dataset shape:", data.shape)

print()
print("Saved as: final_6session_dataset.csv")