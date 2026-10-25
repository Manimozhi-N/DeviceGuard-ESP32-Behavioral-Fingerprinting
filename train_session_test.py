import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# ==============================
# LOAD DATA
# ==============================

phone1 = pd.read_csv("phone_data.csv")
phone2 = pd.read_csv("phone_session2.csv")
phone3 = pd.read_csv("phone_session3.csv")

laptop1 = pd.read_csv("laptop_data.csv")
laptop2 = pd.read_csv("laptop_session2.csv")
laptop3 = pd.read_csv("laptop_session3.csv")


# ==============================
# CLEAN DATA
# ==============================

def clean(data):
    data = data[
        (data["packet_size"] > 0) &
        (data["iat_us"] > 0) &
        (data["packet_frequency"] > 0) &
        (data["rssi"] != 0)
    ].copy()

    data["iat_ms"] = data["iat_us"] / 1000

    return data


phone1 = clean(phone1)
phone2 = clean(phone2)
phone3 = clean(phone3)

laptop1 = clean(laptop1)
laptop2 = clean(laptop2)
laptop3 = clean(laptop3)


# ==============================
# TRAINING DATA
# Session 1 + Session 2
# ==============================

train_data = pd.concat(
    [
        phone1,
        phone2,
        laptop1,
        laptop2
    ],
    ignore_index=True
)


# ==============================
# TEST DATA
# Session 3 ONLY
# ==============================

test_data = pd.concat(
    [
        phone3,
        laptop3
    ],
    ignore_index=True
)


# ==============================
# FEATURES
# ==============================

features = [
    "packet_size",
    "iat_ms",
    "packet_frequency",
    "rssi"
]

X_train = train_data[features]
y_train = train_data["device"]

X_test = test_data[features]
y_test = test_data["device"]


# ==============================
# RANDOM FOREST
# ==============================

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)


# ==============================
# PREDICTION
# ==============================

y_pred = model.predict(X_test)


# ==============================
# RESULTS
# ==============================

accuracy = accuracy_score(y_test, y_pred)

print("======================================")
print("SESSION-BASED DEVICE FINGERPRINTING")
print("======================================")

print()
print("Training data:", len(train_data))
print("Testing data:", len(test_data))

print()
print("Training sessions:")
print("Phone Session 1")
print("Phone Session 2")
print("Laptop Session 1")
print("Laptop Session 2")

print()
print("Testing sessions:")
print("Phone Session 3")
print("Laptop Session 3")

print()
print("Accuracy:", round(accuracy * 100, 2), "%")

print()
print("Classification Report:")
print(classification_report(y_test, y_pred))

print()
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))


# ==============================
# SAVE MODEL
# ==============================

joblib.dump(model, "final_session_model.pkl")

print()
print("Model saved as: final_session_model.pkl")