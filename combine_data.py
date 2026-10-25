import pandas as pd

# Read datasets
phone = pd.read_csv("phone_data.csv")
laptop = pd.read_csv("laptop_data.csv")

# Combine
data = pd.concat([phone, laptop], ignore_index=True)

# Remove rows where packet information is zero
data = data[
    (data["packet_size"] > 0) &
    (data["iat_us"] > 0) &
    (data["packet_frequency"] > 0) &
    (data["rssi"] != 0)
]

# Convert IAT from microseconds to milliseconds
data["iat_ms"] = data["iat_us"] / 1000

# Save cleaned dataset
data.to_csv("real_dataset.csv", index=False)

print("Clean dataset created!")
print()
print(data.head())
print()
print("Dataset shape:", data.shape)
print()
print("Device counts:")
print(data["device"].value_counts())