"""Random forest feature selection on the scikit-learn Wine dataset."""
from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import load_wine
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

OUT = Path(__file__).parent / "results"


def main():
    OUT.mkdir(exist_ok=True)
    data = load_wine()
    x_train, x_test, y_train, y_test = train_test_split(data.data, data.target, test_size=0.25, stratify=data.target, random_state=42)
    full = RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1)
    full.fit(x_train, y_train)
    top = np.argsort(full.feature_importances_)[-5:][::-1]
    small = RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1)
    small.fit(x_train[:, top], y_train)
    def score(model, features):
        pred = model.predict(features)
        return {"accuracy": round(accuracy_score(y_test, pred), 4), "macro_f1": round(f1_score(y_test, pred, average="macro"), 4)}
    result = {"dataset": "scikit-learn Wine", "split": "stratified 75/25, random_state=42", "full_13_features": score(full, x_test), "top_5_features": score(small, x_test[:, top]), "selected_features": [data.feature_names[i] for i in top], "feature_importances": {name: round(float(value), 4) for name, value in zip(data.feature_names, full.feature_importances_)}}
    (OUT / "metrics.json").write_text(json.dumps(result, indent=2) + "\n")
    order = np.argsort(full.feature_importances_)
    plt.figure(figsize=(8, 5))
    plt.barh(np.array(data.feature_names)[order], full.feature_importances_[order])
    plt.xlabel("Impurity-based feature importance")
    plt.tight_layout()
    plt.savefig(OUT / "feature_importance.png", dpi=150)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
