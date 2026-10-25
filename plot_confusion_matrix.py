
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    confusion_matrix,
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report
)

# ==========================================
# SETTINGS
# ==========================================

DATASET_FILE = "session_check_combined.csv"
OUTPUT_FOLDER = Path("results_graphs")
OUTPUT_FOLDER.mkdir(exist_ok=True)

FEATURES = [
    "packet_size",
    "iat_us",
    "packet_frequency",
    "rssi",
    "iat_ms"
]

TEST_SESSIONS = ["Laptop Session 3", "Phone Session 3"]
LABELS = ["Laptop", "Phone"]

# ==========================================
# LOAD AND PREPARE DATA
# ==========================================

df = pd.read_csv(DATASET_FILE)

required = FEATURES[:-1] + ["device", "session_id"]
missing = [col for col in required if col not in df.columns]

if missing:
    raise ValueError(f"Missing columns: {missing}")

for col in FEATURES[:-1]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Calculate milliseconds from microseconds.
df["iat_ms"] = df["iat_us"] / 1000

df = df.dropna(subset=required + ["iat_ms"]).copy()
df = df[df["device"].isin(LABELS)].copy()

# Use complete sessions for the test set.
test_mask = df["session_id"].isin(TEST_SESSIONS)
train = df.loc[~test_mask].copy()
test = df.loc[test_mask].copy()

if train.empty or test.empty:
    raise ValueError("Training or testing data is empty.")

X_train = train[FEATURES]
y_train = train["device"]
X_test = test[FEATURES]
y_test = test["device"]

if set(y_train.unique()) != set(LABELS):
    raise ValueError("Training data must contain Laptop and Phone.")
if set(y_test.unique()) != set(LABELS):
    raise ValueError("Test data must contain Laptop and Phone.")

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

accuracy = accuracy_score(y_test, predictions)

matrix = confusion_matrix(
    y_test,
    predictions,
    labels=LABELS
)

# ==========================================
# SAVE CONFUSION MATRIX GRAPH
# ==========================================

display = ConfusionMatrixDisplay(
    confusion_matrix=matrix,
    display_labels=LABELS
)

fig, ax = plt.subplots(figsize=(7, 6))
display.plot(
    ax=ax,
    cmap="Blues",
    values_format="d",
    colorbar=False
)

ax.set_title(
    f"Session-Based Confusion Matrix\nAccuracy: {accuracy * 100:.2f}%"
)
ax.set_xlabel("Predicted Device")
ax.set_ylabel("Actual Device")

plt.tight_layout()

graph_path = OUTPUT_FOLDER / "confusion_matrix.png"
plt.savefig(graph_path, dpi=200, bbox_inches="tight")
plt.close()

# ==========================================
# SAVE CLASSIFICATION REPORT
# ==========================================

report = classification_report(
    y_test,
    predictions,
    labels=LABELS,
    output_dict=True,
    zero_division=0
)

report_path = OUTPUT_FOLDER / "classification_report.csv"
pd.DataFrame(report).transpose().to_csv(report_path)

print("\n========== EVALUATION FILES SAVED ==========")
print(f"Test samples: {len(y_test)}")
print(f"Accuracy: {accuracy * 100:.2f}%")
print(f"Confusion matrix:\n{matrix}")
print(f"\nGraph: {graph_path}")
print(f"Report: {report_path}")
print("\nOriginal datasets and saved models were not modified.")
