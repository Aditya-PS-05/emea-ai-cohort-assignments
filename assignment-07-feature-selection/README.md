# Assignment 7: random forest feature selection

Run `../.venv/bin/python run.py` from this folder after installing `../requirements-ml.txt`. The script uses the scikit-learn Wine classification dataset. It makes a stratified 75/25 split, trains a 300-tree forest on all 13 features, selects the five largest impurity-based importances from training data, and trains a fresh forest on only those five features. The same held-out test set evaluates both models.

| Features | Test accuracy | Test macro F1 |
| --- | ---: | ---: |
| All 13 | 1.0000 | 1.0000 |
| Top 5 | 1.0000 | 1.0000 |

The selected features are flavanoids, color intensity, proline, alcohol, and hue. The [importance plot](results/feature_importance.png) shows all 13 values; [metrics](results/metrics.json) contains the exact scores. The five-feature model is simpler and easier to inspect, with no measured loss on this one small test split. Perfect accuracy on 45 held-out examples is not a general guarantee. Impurity importance can favor some feature types and can spread credit among correlated inputs.
