
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# ==========================================
# SETTINGS
# ==========================================

DATASET_FILE = "final_filtered_dataset.csv"
TARGET_CANDIDATES = ["device", "label", "target", "class"]

# ==========================================
# LOAD DATASET
# ==========================================

path = Path(DATASET_FILE)

if not path.exists():
    print(f"Dataset not found: {DATASET_FILE}")
    raise SystemExit

df = pd.read_csv(path)

print("\n========== DATASET INFORMATION ==========")
print("Dataset shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())
print("\nFirst five rows:")
print(df.head())
print("\n=========================================")

# Find the target/label column.
target = next(
    (column for column in TARGET_CANDIDATES if column in df.columns),
    None
)

if target is None:
    print("\nCould not identify the device label column.")
    print("Check the printed column names and update TARGET_CANDIDATES.")
    raise SystemExit

# Remove rows with missing target labels.
df = df.dropna(subset=[target]).copy()

# Exclude labels and non-feature identifiers from the input features.
excluded = {
    target.lower(),
    "timestamp",
    "session",
    "session_id",
    "record_number",
    "device_id",
    "mac",
    "mac_address",
    "status",
    "confidence"
}

feature_columns = [
    column for column in df.columns
    if column.lower() not in excluded
    and pd.api.types.is_numeric_dtype(df[column])
]

if not feature_columns:
    print("\nNo numeric feature columns found.")
    print("Inspect the columns printed above before continuing.")
    raise SystemExit

X = df[feature_columns].replace(
    [float("inf"), float("-inf")], float("nan")
)

y = df[target]

# Remove rows with missing feature values.
valid_rows = X.notna().all(axis=1)
X = X.loc[valid_rows]
y = y.loc[valid_rows]

if y.nunique() < 2:
    print("\nAt least two device classes are needed for evaluation.")
    raise SystemExit

print("\nTarget column:", target)
print("Feature columns:", feature_columns)
print("\nSamples per class:")
print(y.value_counts().to_string())

# ==========================================
# RANDOM STRATIFIED HOLDOUT EVALUATION
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)
predictions = model.predict(X_test)

print("\n========== MODEL EVALUATION ==========")
print("Training samples:", len(X_train))
print("Test samples:", len(X_test))
print(f"Accuracy: {accuracy_score(y_test, predictions) * 100:.2f}%")

print("\nClassification report:")
print(classification_report(y_test, predictions, zero_division=0))

print("Confusion matrix:")
print("Class order:", model.classes_.tolist())
print(confusion_matrix(y_test, predictions, labels=model.classes_))

print("\nIMPORTANT:")
print("This is a random holdout evaluation, not a session-separated test.")
print("Related samples from the same recording session may appear in both")
print("training and test sets, so this result may overestimate generalization.")
print("This newly trained model is for evaluation only; your saved models")
print("have not been modified.")
