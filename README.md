# EMEA AI Cohort assignments

Assignments 1, 4, 6, 8, 9, 11, and 12 were treated as complete for this work. Their upstream study projects are listed in [UPSTREAM.md](UPSTREAM.md).

Original submissions for the remaining assignments:

| Assignment | Folder | Run |
| --- | --- | --- |
| 2: nonlinear regression | `assignment-02-regression` | `python run.py` |
| 3: PCA and classifiers | `assignment-03-pca` | `python run.py` |
| 5: single-layer perceptron | `assignment-05-perceptron` | `python run.py` |
| 7: random forest feature selection | `assignment-07-feature-selection` | `python run.py` |
| 10: local text summarizer | `assignment-10-summarizer` | `uvicorn app:app --reload` |

For assignments 2, 3, 5, and 7, install `requirements-ml.txt` in a Python 3.12 environment. Each script writes its measured metrics and plot(s) to its own `results/` directory. Assignments 2 and 3 fetch their UCI datasets on first run.

Assignment 10 has its own `environment.yml` and README. A Conda-compatible environment is available at `.mamba/envs/emea-summarizer`, and `tinyllama` is installed in local Ollama. Ollama must be running when the app generates a summary.

The upstream projects are examples, not original submissions or proof that every assignment requirement was met. See [UPSTREAM.md](UPSTREAM.md) for provenance and assignment gaps.
