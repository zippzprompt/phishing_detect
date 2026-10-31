"""
Retrain versi ringan dari model Random Forest skripsi (n_estimators=10,
max_depth=5, criterion='gini', random_state=0) hanya menggunakan top-15
fitur berdasarkan Mean |SHAP Value| kelas phishing, yang dipilih karena
bisa dihitung langsung dari URL + HTML halaman tanpa butuh tabel statistik
dari data training (mis. TLDLegitimateProb, URLCharProb).

Jalankan dari dalam folder model/:
    python train_lightweight_model.py
"""

import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

TOP_FEATURES = [
    "URLSimilarityIndex",
    "NoOfExternalRef",
    "LineOfCode",
    "NoOfSelfRef",
    "NoOfImage",
    "HasSubmitButton",
    "NoOfJS",
    "HasCopyrightInfo",
    "URLTitleMatchScore",
    "HasSocialNet",
    "NoOfCSS",
    "IsResponsive",
    "URLLength",
    "HasFavicon",
    "IsHTTPS"
]

df = pd.read_csv("train_subset.csv")
X = df[TOP_FEATURES]
y = df["Label"]  # 1 = Legitimate, 0 = Phishing (sama seperti skripsi)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=0, stratify=y
)

rf = RandomForestClassifier(
    n_estimators=10,
    max_depth=5,
    random_state=0,
    criterion="gini",
)
rf.fit(X_train, y_train)

y_pred = rf.predict(X_test)

metrics = {
    "accuracy": accuracy_score(y_test, y_pred),
    "precision": precision_score(y_test, y_pred),
    "recall": recall_score(y_test, y_pred),
    "f1_score": f1_score(y_test, y_pred),
    "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
    "n_features": len(TOP_FEATURES),
    "features": TOP_FEATURES,
}

print(classification_report(y_test, y_pred, target_names=["Phishing", "Legitimate"]))
print("Confusion matrix (rows=true, cols=pred, order=[Phishing, Legitimate]):")
print(confusion_matrix(y_test, y_pred))

joblib.dump(rf, "phishing_rf_lite.joblib")
with open("feature_names.json", "w") as f:
    json.dump(TOP_FEATURES, f, indent=2)
with open("metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

print("\nModel tersimpan: phishing_rf_lite.joblib")
print("Daftar fitur tersimpan: feature_names.json")
print("Metrik evaluasi tersimpan: metrics.json")
