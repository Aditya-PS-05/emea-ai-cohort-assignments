"""One-layer Keras classifier on the breast-cancer diagnostic dataset."""
from pathlib import Path
import json
import os

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from sklearn.datasets import load_breast_cancer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

OUT = Path(__file__).parent / "results"


def main():
    OUT.mkdir(exist_ok=True)
    tf.keras.utils.set_random_seed(42)
    data = load_breast_cancer()
    x_train, x_test, y_train, y_test = train_test_split(data.data, data.target, test_size=0.2, stratify=data.target, random_state=42)
    scaler = StandardScaler()
    x_train = scaler.fit_transform(x_train)
    x_test = scaler.transform(x_test)
    model = tf.keras.Sequential([tf.keras.Input(shape=(x_train.shape[1],)), tf.keras.layers.Dense(1, activation="sigmoid")])
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), loss="binary_crossentropy", metrics=["accuracy"])
    history = model.fit(x_train, y_train, validation_split=0.2, epochs=25, batch_size=32, verbose=0)
    pred = (model.predict(x_test, verbose=0).ravel() >= 0.5).astype(int)
    result = {"dataset": "scikit-learn Breast Cancer Wisconsin Diagnostic", "architecture": "30 inputs -> 1 sigmoid output; no hidden layer", "epochs": 25, "positive_class": "benign", "test": {"accuracy": round(accuracy_score(y_test, pred), 4), "precision": round(precision_score(y_test, pred), 4), "recall": round(recall_score(y_test, pred), 4), "f1": round(f1_score(y_test, pred), 4)}, "final_train_loss": round(history.history["loss"][-1], 4), "final_validation_loss": round(history.history["val_loss"][-1], 4)}
    (OUT / "metrics.json").write_text(json.dumps(result, indent=2) + "\n")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, key, label in ((axes[0], "loss", "Binary cross-entropy"), (axes[1], "accuracy", "Accuracy")):
        ax.plot(history.history[key], label="train")
        ax.plot(history.history["val_" + key], label="validation")
        ax.set_xlabel("Epoch")
        ax.set_ylabel(label)
        ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "training_history.png", dpi=150)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
