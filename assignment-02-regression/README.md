# Assignment 2: nonlinear regression and regularization

Run `../.venv/bin/python run.py` from this folder after installing `../requirements-ml.txt`. The script downloads the [UCI Energy Efficiency dataset](https://archive.ics.uci.edu/dataset/242/energy+efficiency), predicts heating load from eight building features, and writes [metrics](results/metrics.json) and an [RMSE plot](results/rmse_comparison.png). The dataset contains 768 rows. The same 80/20 random split is used for every model; preprocessing is fitted only on training data.

| Model | Train RMSE | Test RMSE | Test R² |
| --- | ---: | ---: | ---: |
| Linear | 2.8931 | 3.0254 | 0.9122 |
| Polynomial degree 2 | 0.6977 | 0.8030 | 0.9938 |
| Polynomial degree 3 | 0.4045 | 0.5429 | 0.9972 |
| Ridge, degree 2, α=10 | 2.5129 | 2.6794 | 0.9311 |
| Lasso, degree 2, α=0.05 | 2.5557 | 2.7390 | 0.9280 |

MSE is the mean squared prediction error in squared heating-load units; RMSE is its square root in heating-load units; R² measures improvement over predicting the test-set mean. The plain linear model underfits relative to both polynomial models. Degree 3 has the lowest test RMSE, though its train/test gap is larger than degree 2. The chosen Ridge and Lasso penalties substantially worsen degree-2 accuracy, so these strengths are too aggressive here. No degree tested showed severe overfitting on this split. These values are from one split, not a cross-validation estimate.

Among the 44 degree-2 coefficients, Ridge keeps all 44 nonzero and reduces their L2 norm from 57,059.6 to 4.87. Lasso leaves 13 nonzero coefficients, making the model sparser. The very large unregularized norm reflects instability from correlated polynomial terms; neither chosen penalty improved held-out error.
