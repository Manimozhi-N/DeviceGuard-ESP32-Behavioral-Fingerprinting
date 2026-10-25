
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)
from pathlib import Path

# ==========================================
# SETTINGS
# ==========================================

DATASET_FILE = "session_check_combined.csv"

FEATURES = [
    "packet_size",
    "iat_us",
    "packet_frequency",
    "rssi",
    "iat_ms"
]

TARGET = "device"
SESSION = "session_id"

# Hold out Session 3 for each device.
TEST_SESSIONS = [
    "Phone Session 3",
    "Laptop Session 3"
]

# ==========================================
# LOAD DATASET
# ==========================================

if not Path(DATASET_FILE).exists():
    print(f"ERROR: {DATASET_FILE} not found.")
    print("Run python check_sessions.py first.")
    raise SystemExit

df = pd.read_csv(DATASET_FILE)

print("\n========== DATASET INFORMATION ==========")
print("Dataset shape:", df.shape)
print("Columns:", df.columns.tolist())

required_source_columns = [
    "packet_size",
    "iat_us",
    "packet_frequency",
    "rssi",
    TARGET,
    SESSION
]

missing = [
    column for column in required_source_columns
    if column not in df.columns
]

if missing:
    print("\nMissing required columns:", missing)
    raise SystemExit

# ==========================================
# CLEAN AND PREPARE DATA
# ==========================================

numeric_columns = [
    "packet_size",
    "iat_us",
    "packet_frequency",
    "rssi"
]

for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

# Convert microseconds to milliseconds.
# 1 millisecond = 1000 microseconds.
df["iat_ms"] = df["iat_us"] / 1000

# Remove rows with missing values.
df = df.dropna(
    subset=required_source_columns + ["iat_ms"]
).copy()

# Keep the intended device classes only.
df = df[df[TARGET].isin(["Laptop", "Phone"])].copy()

print("\nTotal valid records:", len(df))

print("\nRecords by device:")
print(df[TARGET].value_counts().to_string())

print("\nRecords by session:")
print(df[SESSION].value_counts().to_string())

# ==========================================
# SPLIT BY COMPLETE RECORDING SESSIONS
# ==========================================

available_sessions = set(df[SESSION].astype(str))
missing_sessions = set(TEST_SESSIONS) - available_sessions

if missing_sessions:
    print("\nERROR: Expected test sessions not found:")
    print(sorted(missing_sessions))
    print("\nAvailable sessions:")
    print(sorted(available_sessions))
    raise SystemExit

test_mask = df[SESSION].isin(TEST_SESSIONS)

train = df.loc[~test_mask].copy()
test = df.loc[test_mask].copy()

if train.empty or test.empty:
    print("\nERROR: Training or testing data is empty.")
    raise SystemExit

X_train = train[FEATURES].copy()
y_train = train[TARGET].copy()

X_test = test[FEATURES].copy()
y_test = test[TARGET].copy()

if y_train.nunique() < 2:
    print("\nERROR: Training data needs both device classes.")
    raise SystemExit

if y_test.nunique() < 2:
    print("\nERROR: Test data needs both device classes.")
    raise SystemExit

print("\n========== SESSION SPLIT ==========")

print("Training sessions:")
print(sorted(train[SESSION].unique()))

print("\nTesting sessions:")
print(sorted(test[SESSION].unique()))

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))

print("\nTraining class counts:")
print(y_train.value_counts().to_string())

print("\nTesting class counts:")
print(y_test.value_counts().to_string())

# ==========================================
# TRAIN RANDOM FOREST
# ==========================================

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)

# Predict only on the held-out sessions.
predictions = model.predict(X_test)

# ==========================================
# EVALUATION RESULTS
# ==========================================

accuracy = accuracy_score(y_test, predictions)

print("\n========== SESSION-BASED RESULTS ==========")

print(f"\nAccuracy: {accuracy * 100:.2f}%")

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        predictions,
        labels=["Laptop", "Phone"],
        zero_division=0
    )
)

print("\nConfusion Matrix")
print("Rows = Actual; Columns = Predicted")
print("Class order: ['Laptop', 'Phone']")

matrix = confusion_matrix(
    y_test,
    predictions,
    labels=["Laptop", "Phone"]
)

print(matrix)

print("\nCorrect predictions:", (y_test == predictions).sum())
print("Incorrect predictions:", (y_test != predictions).sum())

print("\n========== INTERPRETATION ==========")
print(
    "This model was trained on Laptop Sessions 1-2 and "
    "Phone Sessions 1-2."
)
print(
    "It was tested on Laptop Session 3 and Phone Session 3."
)
print(
    "This is a session-separated evaluation of a newly trained model."
)
print(
    "It does not replace or modify your saved model files."
)
print(
    "Results apply to these recordings and do not guarantee "
    "performance on every device or network."
)
print("====================================")
