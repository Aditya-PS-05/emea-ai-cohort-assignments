"""UCI Energy Efficiency: linear and regularized polynomial regression."""
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

URL = "https://archive.ics.uci.edu/static/public/242/energy+efficiency.zip"
OUT = Path(__file__).parent / "results"


def load_data():
    response = requests.get(URL, timeout=30)
    response.raise_for_status()
    with ZipFile(BytesIO(response.content)) as archive:
        filename = next(name for name in archive.namelist() if name.lower().endswith(".xlsx"))
        frame = pd.read_excel(BytesIO(archive.read(filename)))
    frame = frame.iloc[:, :10].apply(pd.to_numeric, errors="coerce")
    frame = frame.dropna(subset=[frame.columns[8]])
    return frame.iloc[:, :8], frame.iloc[:, 8]


def metrics(model, x_train, x_test, y_train, y_test):
    model.fit(x_train, y_train)
    def score(x, y):
        pred = model.predict(x)
        mse = mean_squared_error(y, pred)
        return {"mse": round(mse, 4), "rmse": round(float(np.sqrt(mse)), 4), "r2": round(r2_score(y, pred), 4)}
    coefficients = model.steps[-1][1].coef_
    return {"train": score(x_train, y_train), "test": score(x_test, y_test), "nonzero_coefficients": int(np.count_nonzero(np.abs(coefficients) > 1e-8)), "coefficient_l2_norm": round(float(np.linalg.norm(coefficients)), 4)}


def main():
    OUT.mkdir(exist_ok=True)
    x, y = load_data()
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
    results = {"dataset": "UCI Energy Efficiency", "target": "Heating Load", "rows": len(x), "split": "80/20, random_state=42", "models": {}}
    for degree in (1, 2, 3):
        model = make_pipeline(SimpleImputer(strategy="median"), PolynomialFeatures(degree, include_bias=False), StandardScaler(), LinearRegression())
        results["models"][f"linear_degree_{degree}"] = metrics(model, x_train, x_test, y_train, y_test)
    for name, estimator in (("ridge_degree_2", Ridge(alpha=10)), ("lasso_degree_2", Lasso(alpha=0.05, max_iter=50000))):
        model = make_pipeline(SimpleImputer(strategy="median"), PolynomialFeatures(2, include_bias=False), StandardScaler(), estimator)
        results["models"][name] = metrics(model, x_train, x_test, y_train, y_test)
    (OUT / "metrics.json").write_text(json.dumps(results, indent=2) + "\n")
    labels = list(results["models"])
    plt.figure(figsize=(9, 5))
    plt.plot(labels, [results["models"][n]["train"]["rmse"] for n in labels], "o-", label="train")
    plt.plot(labels, [results["models"][n]["test"]["rmse"] for n in labels], "o-", label="test")
    plt.ylabel("RMSE (heating load)")
    plt.xticks(rotation=25, ha="right")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT / "rmse_comparison.png", dpi=150)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
