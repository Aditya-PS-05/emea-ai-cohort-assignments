"""PCA and classifier comparison on UCI red wine quality."""
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

URL = "https://archive.ics.uci.edu/static/public/186/wine+quality.zip"
OUT = Path(__file__).parent / "results"


def load_data():
    response = requests.get(URL, timeout=30)
    response.raise_for_status()
    with ZipFile(BytesIO(response.content)) as archive:
        name = next(name for name in archive.namelist() if name.endswith("winequality-red.csv"))
        frame = pd.read_csv(BytesIO(archive.read(name)), sep=";")
    frame = frame.drop_duplicates()
    return frame.drop(columns="quality"), (frame.quality >= 6).astype(int)


def main():
    OUT.mkdir(exist_ok=True)
    x, y = load_data()
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42, stratify=y)
    prep = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), PCA(n_components=0.95))
    train_pc = prep.fit_transform(x_train)
    test_pc = prep.transform(x_test)
    pca = prep.named_steps["pca"]
    results = {"dataset": "UCI Wine Quality, red", "target": "quality >= 6", "rows_after_deduplication": len(x), "split": "stratified 80/20, random_state=42", "components": int(pca.n_components_), "explained_variance_ratio": [round(float(v), 4) for v in pca.explained_variance_ratio_], "models": {}}
    for name, model in (("logistic_regression", LogisticRegression(max_iter=1000)), ("knn", KNeighborsClassifier(n_neighbors=7)), ("gaussian_nb", GaussianNB())):
        model.fit(train_pc, y_train)
        pred = model.predict(test_pc)
        precision, recall, f1, _ = precision_recall_fscore_support(y_test, pred, average="macro", zero_division=0)
        results["models"][name] = {"accuracy": round(accuracy_score(y_test, pred), 4), "macro_precision": round(precision, 4), "macro_recall": round(recall, 4), "macro_f1": round(f1, 4)}
    results["best_by_test_macro_f1"] = max(results["models"], key=lambda name: results["models"][name]["macro_f1"])
    (OUT / "metrics.json").write_text(json.dumps(results, indent=2) + "\n")
    plt.figure(figsize=(7, 4))
    plt.plot(np.arange(1, len(pca.explained_variance_ratio_) + 1), np.cumsum(pca.explained_variance_ratio_), "o-")
    plt.xlabel("Number of principal components")
    plt.ylabel("Cumulative explained variance")
    plt.ylim(0, 1.05)
    plt.tight_layout()
    plt.savefig(OUT / "explained_variance.png", dpi=150)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
