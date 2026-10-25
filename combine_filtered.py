import pandas as pd

# Load phone data
phone = pd.read_csv("phone_filtered_session.csv")

# Load laptop data
laptop = pd.read_csv("laptop_filtered_session.csv")

# Combine both datasets
final_data = pd.concat(
    [phone, laptop],
    ignore_index=True
)

# Remove empty rows
final_data = final_data.dropna()

# Save final dataset
final_data.to_csv(
    "final_filtered_dataset.csv",
    index=False
)

print("======================================")
print("FINAL FILTERED DATASET CREATED")
print("======================================")

print()
print("Phone samples:", len(phone))
print("Laptop samples:", len(laptop))
print("Total samples:", len(final_data))

print()
print("Device counts:")
print(final_data["device"].value_counts())

print()
print("Dataset shape:", final_data.shape)

print()
print("First 5 rows:")
print(final_data.head())

print()
print("Saved as: final_filtered_dataset.csv")