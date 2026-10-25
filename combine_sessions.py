import pandas as pd

# Read all four sessions
phone1 = pd.read_csv("phone_data.csv")
phone2 = pd.read_csv("phone_session2.csv")

laptop1 = pd.read_csv("laptop_data.csv")
laptop2 = pd.read_csv("laptop_session2.csv")

# Combine everything
data = pd.concat(
    [phone1, phone2, laptop1, laptop2],
    ignore_index=True
)

# Remove invalid rows
data = data[
    (data["packet_size"] > 0) &
    (data["iat_us"] > 0) &
    (data["packet_frequency"] > 0) &
    (data["rssi"] != 0)
].copy()

# Convert IAT from microseconds to milliseconds
data["iat_ms"] = data["iat_us"] / 1000

# Save final dataset
data.to_csv("final_real_dataset.csv", index=False)

print("================================")
print("FINAL REAL DATASET CREATED")
print("================================")

print("Total samples:", len(data))

print()
print("Device counts:")
print(data["device"].value_counts())

print()
print("Dataset shape:", data.shape)

print()
print("First 5 rows:")
print(data.head())