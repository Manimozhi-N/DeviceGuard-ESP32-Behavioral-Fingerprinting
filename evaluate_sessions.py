
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
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

DATASET_FILE = "final_6session_dataset.csv"

# ==========================================
# LOAD DATA
# ==========================================

if not Path(DATASET_FILE).exists():
    print("Dataset file not found:", DATASET_FILE)
    raise SystemExit

df = pd.read_csv(DATASET_FILE)

print("Dataset shape:", df.shape)
print("Columns:", df.columns.tolist())

# The screenshot shows these columns in your dataset.
target_column = "device"

feature_columns = [
    "packet_size",
    "iat_us",
    "packet_frequency",
    "rssi",
    "iat_ms"
]

required_columns = feature_columns + [target_column]

missing = [c for c in required_columns if c not in df.columns]

if missing:
    print("Missing columns:", missing)
    raise SystemExit

df = df.dropna(subset=required_columns).copy()

X = df[feature_columns].apply(pd.to_numeric, errors="coerce")
y = df[target_column].astype(str)

valid = X.notna().all(axis=1)
X = X.loc[valid]
y = y.loc[valid]

print("\nSamples per device:")
print(y.value_counts())

# ==========================================
# CHECK WHETHER SESSION LABELS EXIST
# ==========================================

possible_group_columns = [
    "session",
    "session_id",
    "recording_session",
    "session_name"
]

group_column = next(
    (c for c in possible_group_columns if c in df.columns),
    None
)

if group_column is None:
    print(
        "\nSTOP: No session ID column was found in this dataset."
    )
    print(
        "A genuinely session-separated evaluation needs a reliable "
        "recording-session label for every row."
    )
    print(
        "Do not treat a random split as a session-separated test."
    )
    raise SystemExit

groups = df.loc[X.index, group_column]

if groups.nunique() < 2:
    print("At least two distinct sessions are needed.")
    raise SystemExit

# ==========================================
# SPLIT BY SESSION
# ==========================================

splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.25,
    random_state=42
)

train_idx, test_idx = next(
    splitter.split(X, y, groups=groups)
)

X_train = X.iloc[train_idx]
X_test = X.iloc[test_idx]
y_train = y.iloc[train_idx]
y_test = y.iloc[test_idx]

print("\nTraining sessions:")
print(sorted(groups.iloc[train_idx].astype(str).unique()))

print("\nTesting sessions:")
print(sorted(groups.iloc[test_idx].astype(str).unique()))

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))

if y_train.nunique() < 2:
    print(
        "\nTraining split contains only one device class. "
        "Choose different session groups before evaluating."
    )
    raise SystemExit

# ==========================================
# TRAIN AND EVALUATE
# ==========================================

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)
predictions = model.predict(X_test)

print("\n========== SESSION-BASED RESULTS ==========")

print(
    f"Accuracy: {accuracy_score(y_test, predictions) * 100:.2f}%"
)

print("\nClassification report:")
print(
    classification_report(
        y_test,
        predictions,
        zero_division=0
    )
)

labels = sorted(y.unique())

print("Class order:", labels)
print("Confusion matrix:")
print(confusion_matrix(y_test, predictions, labels=labels))

print("\nNote:")
print(
    "This evaluation is only genuinely session-separated if the "
    "session labels correctly represent the original recordings."
)
