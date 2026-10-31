"""
Aplikasi Flask: Sistem Deteksi Phishing Website
Interface untuk model Random Forest ringan (top-15 fitur SHAP) hasil skripsi.

Jalankan:
    python app.py
Lalu buka http://127.0.0.1:5000 di browser.
"""

import base64
import io
import json
import os

import joblib
import matplotlib
matplotlib.use("Agg")  # backend non-GUI, wajib untuk server Flask
import matplotlib.pyplot as plt
import pandas as pd
import shap
from flask import Flask, render_template, request

from feature_extraction import extract_features, FEATURE_ORDER

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "phishing_rf_lite.joblib")
FEATURES_PATH = os.path.join(BASE_DIR, "model", "feature_names.json")

app = Flask(__name__)

# --- load model & explainer sekali saat startup (bukan tiap request) ---
model = joblib.load(MODEL_PATH)
with open(FEATURES_PATH) as f:
    MODEL_FEATURES = json.load(f)

explainer = shap.TreeExplainer(model)

LABEL_NAMES = {0: "Phishing", 1: "Legitimate"}


def make_waterfall_plot(shap_values_single, base_value, feature_values, feature_names):
    """Bikin SHAP waterfall plot untuk satu prediksi, dikembalikan sebagai
    base64 PNG string supaya bisa langsung ditaruh di tag <img> HTML."""
    explanation = shap.Explanation(
        values=shap_values_single,
        base_values=base_value,
        data=feature_values,
        feature_names=feature_names,
    )
    plt.figure()
    shap.plots.waterfall(explanation, show=False)
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


SIMILARITY_LOW_THRESHOLD = 80    # di bawah ini -> indikasi kuat phishing (peniruan brand terdeteksi)

@app.route("/predict", methods=["POST"])
def predict():
    raw_url = request.form.get("url", "").strip()
    if not raw_url:
        return render_template("index.html", error="Masukkan URL terlebih dahulu.")

    try:
        features, warning = extract_features(raw_url)
    except Exception as exc:
        return render_template("index.html", error=f"Gagal memproses URL: {exc}")

    X_row = pd.DataFrame([features], columns=MODEL_FEATURES)

    # --- Lapis 1: hasil murni dari model Random Forest ---
    model_pred_class = int(model.predict(X_row)[0])
    pred_proba = model.predict_proba(X_row)[0]
    model_label = LABEL_NAMES[model_pred_class]
    model_confidence = round(float(pred_proba[model_pred_class]) * 100, 2)

    # --- Lapis 2: aturan berbasis URLSimilarityIndex ---
    similarity_score = features.get("URLSimilarityIndex", 100)
    domain_flagged_phishing = similarity_score < SIMILARITY_LOW_THRESHOLD
    domain_verified_legitimate = similarity_score >= SIMILARITY_LOW_THRESHOLD

    if domain_flagged_phishing:
        final_is_phishing = True
    elif domain_verified_legitimate:
        final_is_phishing = False
    else:
        final_is_phishing = (model_pred_class == 0)

    final_label = "Phishing" if final_is_phishing else "Legitimate"
    # SHAP tetap dihitung untuk keputusan MODEL (bukan verdict akhir gabungan),
    # supaya penjelasan waterfall plot tetap konsisten dengan cara model
    # itu sendiri mengambil keputusan
    sv = explainer(X_row)
    shap_vals_pred_class = sv.values[0, :, model_pred_class]
    base_value_pred_class = sv.base_values[0, model_pred_class]
    plot_b64 = make_waterfall_plot(
        shap_vals_pred_class, base_value_pred_class,
        X_row.iloc[0].values, MODEL_FEATURES,
    )

    return render_template(
        "result.html",
        url=raw_url,
        label=final_label,
        is_phishing=final_is_phishing,
        model_label=model_label,
        model_confidence=model_confidence,
        domain_flagged=domain_flagged_phishing,
        similarity_score=similarity_score,
        features=features,
        warning=warning,
        plot_b64=plot_b64,
    )

if __name__ == "__main__":
    app.run(debug=True, threaded=False)
