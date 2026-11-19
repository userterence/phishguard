import os, sys, joblib, pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from app.features import FEATURE_ORDER

HERE = os.path.dirname(__file__)

def main():
    df = pd.read_csv(os.path.join(HERE, "dataset.csv"))
    X = df[FEATURE_ORDER].values
    y = df["label"].values
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    clf = RandomForestClassifier(n_estimators=300, max_depth=None,
                                 min_samples_leaf=1, n_jobs=-1, random_state=42)
    clf.fit(Xtr, ytr)

    pred = clf.predict(Xte)
    print("Accuracy:", round(accuracy_score(yte, pred), 4))
    print(classification_report(yte, pred, target_names=["safe","suspicious","phishing"]))

    joblib.dump(clf, os.path.join(HERE, "model.pkl"))
    print("Saved -> ml/model.pkl")

if __name__ == "__main__":
    main()
