import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Load windowed dataset
data = pd.read_csv("windowed_dataset.csv")

# Features
X = data[
    [
        "mean_packet_size",
        "std_packet_size",
        "mean_iat_ms",
        "std_iat_ms",
        "mean_packet_frequency",
        "mean_rssi"
    ]
]

# Target
y = data["device"]

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Random Forest
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# Train
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)

# Accuracy
accuracy = accuracy_score(y_test, y_pred)

print("======================================")
print("WINDOW-BASED RANDOM FOREST")
print("======================================")

print("Total windows:", len(data))
print("Training windows:", len(X_train))
print("Testing windows:", len(X_test))

print()
print("Accuracy:", round(accuracy * 100, 2), "%")

print()
print("Classification Report:")
print(classification_report(y_test, y_pred))

print()
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Save model
joblib.dump(model, "window_device_model.pkl")

print()
print("Model saved as: window_device_model.pkl")