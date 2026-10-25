import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Load final real dataset
data = pd.read_csv("final_real_dataset.csv")

# Features
X = data[
    [
        "packet_size",
        "iat_ms",
        "packet_frequency",
        "rssi"
    ]
]

# Target
y = data["device"]

# Split data
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

print("========================================")
print("FINAL REAL DATASET - RANDOM FOREST")
print("========================================")

print("Total samples:", len(data))
print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

print()
print("Accuracy:", accuracy)
print("Accuracy percentage:", round(accuracy * 100, 2), "%")

print()
print("Classification Report:")
print(classification_report(y_test, y_pred))

print()
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Save final model
joblib.dump(model, "final_device_model.pkl")

print()
print("Model saved as: final_device_model.pkl")