# Assignment 5: single-layer perceptron

Run `../.venv/bin/python run.py` from this folder after installing `../requirements-ml.txt`. The script uses the scikit-learn Breast Cancer Wisconsin Diagnostic dataset as a binary classification task. It holds out a stratified 20% test set, standardizes using training data, and trains one Keras `Dense(1, activation="sigmoid")` output with no hidden layer for exactly 25 epochs. A 20% validation fraction comes from the training portion.

The sigmoid turns the weighted sum of 30 input features into a probability between 0 and 1. Binary cross-entropy penalizes incorrect confident probabilities; Adam updates the weights using gradients; each epoch passes over the training data once. `results/metrics.json` and `results/training_history.png` are produced by the run.

On the held-out test set, accuracy was 0.8947, benign-class precision 0.9412, recall 0.8889, and F1 0.9143. Final training loss was 0.2584 and validation loss 0.2474. These values come from one split and one training run.

This dataset is used to demonstrate a classifier, not for medical diagnosis. The metrics treat the dataset's benign label as the positive class.
