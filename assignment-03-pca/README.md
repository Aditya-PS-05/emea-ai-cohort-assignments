# Assignment 3: PCA and classifier comparison

Run `../.venv/bin/python run.py` from this folder after installing `../requirements-ml.txt`. The script downloads the red-wine file from the [UCI Wine Quality dataset](https://archive.ics.uci.edu/dataset/186/wine+quality), removes duplicate rows, and classifies a wine as quality 6 or above versus below 6. This binary target avoids treating the small extreme-score groups as well measured classes. The stratified train/test split is 80/20 with seed 42. Median imputation, scaling, and PCA are fitted to training data only.

Nine of 11 principal components retain 97.78% of the training variance, exceeding the 95% selection threshold. PCA rotates the standardized input into uncorrelated axes; it does not use the quality labels. See the [variance plot](results/explained_variance.png) and [metrics](results/metrics.json).

| Classifier | Accuracy | Macro precision | Macro recall | Macro F1 |
| --- | ---: | ---: | ---: | ---: |
| Logistic regression | 0.7316 | 0.7311 | 0.7318 | 0.7312 |
| K-nearest neighbors, k=7 | 0.7206 | 0.7202 | 0.7179 | 0.7184 |
| Gaussian Naive Bayes | 0.7500 | 0.7496 | 0.7478 | 0.7484 |

Macro metrics average the two classes equally. Gaussian Naive Bayes performs best on this test split by macro F1 (0.7484). The ranking is descriptive: selecting a model on the test set makes that score optimistic as a model-selection estimate. A fresh holdout or cross-validation would be needed before claiming it generalizes best.
