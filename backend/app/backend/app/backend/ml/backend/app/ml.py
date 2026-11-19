import os, joblib, numpy as np
from .features import vectorize, extract_features, detect_category, explain

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ml", "model.pkl")
_model = None
LABELS = {0: "safe", 1: "suspicious", 2: "phishing"}

def load_model():
    global _model
    if _model is None and os.path.exists(MODEL_PATH):
        _model = joblib.load(MODEL_PATH)
    return _model

def classify(url: str) -> dict:
    feats = extract_features(url)
    model = load_model()

    if model is not None:
        x = np.array([vectorize(url)])
        probs = model.predict_proba(x)[0]
        idx = int(np.argmax(probs))
        status = LABELS[idx]
        confidence = round(float(probs[idx]), 4)
    else:
        # Fallback heuristic if no trained model is present (clearly marked as heuristic)
        score = (feats["has_ip"]*3 + feats["has_at"]*3 + (feats["num_hyphens"]>=3)*2
                 + (feats["num_subdomains"]>=3)*2 + (feats["suspicious_words"]>=2)*2
                 + feats["punycode"]*2 + (feats["has_https"]==0)*1)
        status = "phishing" if score >= 8 else "suspicious" if score >= 4 else "safe"
        confidence = None   # heuristic score is NOT a probability

    category = detect_category(url) if status != "safe" else "none"
    return {
        "status": status,
        "category": category,
        "confidence": confidence,
        "reasons": explain(feats, status),
    }
