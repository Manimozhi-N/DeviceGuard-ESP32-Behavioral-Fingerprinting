import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

print("======================================")
print("FINAL FILTERED RANDOM FOREST MODEL")
print("======================================")

# Load real filtered dataset
df = pd.read_csv("final_filtered_dataset.csv")

print("Total samples:", len(df))

print("\nDevice counts:")
print(df["device"].value_counts())

# Features
features = [
    "packet_size",
    "iat_us",
    "packet_frequency",
    "rssi"
]

X = df[features]
y = df["device"]

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))

# Create Random Forest
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

print("\nAccuracy:", round(accuracy * 100, 2), "%")

# Classification report
print("\nClassification Report:")
print(
    classification_report(
        y_test,
        y_pred
    )
)

# Confusion matrix
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Save model
joblib.dump(
    model,
    "final_filtered_model.pkl"
)

print("\nModel saved as: final_filtered_model.pkl")