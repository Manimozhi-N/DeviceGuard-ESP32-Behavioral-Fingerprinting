import pandas as pd

# All four real sessions
files = [
    "phone_data.csv",
    "phone_session2.csv",
    "laptop_data.csv",
    "laptop_session2.csv"
]

window_size = 5
windowed_data = []

for file in files:

    data = pd.read_csv(file)

    # Remove invalid rows
    data = data[
        (data["packet_size"] > 0) &
        (data["iat_us"] > 0) &
        (data["packet_frequency"] > 0) &
        (data["rssi"] != 0)
    ].copy()

    # Convert IAT to milliseconds
    data["iat_ms"] = data["iat_us"] / 1000

    # Create 5-row behavioral windows
    for start in range(0, len(data) - window_size + 1, window_size):

        window = data.iloc[start:start + window_size]

        # Calculate behavioral features
        row = {
            "mean_packet_size": window["packet_size"].mean(),
            "std_packet_size": window["packet_size"].std(),
            "mean_iat_ms": window["iat_ms"].mean(),
            "std_iat_ms": window["iat_ms"].std(),
            "mean_packet_frequency": window["packet_frequency"].mean(),
            "mean_rssi": window["rssi"].mean(),
            "device": window["device"].iloc[0]
        }

        windowed_data.append(row)

# Create final window dataset
result = pd.DataFrame(windowed_data)

# Replace NaN standard deviation values
result = result.fillna(0)

# Save
result.to_csv("windowed_dataset.csv", index=False)

print("====================================")
print("WINDOWED BEHAVIORAL DATASET")
print("====================================")

print("Total behavioral windows:", len(result))

print()
print("Device counts:")
print(result["device"].value_counts())

print()
print("Features:")
print(result.columns.tolist())

print()
print("First 5 windows:")
print(result.head())

print()
print("Saved as: windowed_dataset.csv")