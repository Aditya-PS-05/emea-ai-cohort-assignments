# EMEA AI Cohort assignments

| Assignment | Folder | Run / guide |
| --- | --- | --- |
| 1: End-to-End Machine Learning Pipeline | `assignment-01-uci-pipeline` | See upstream README |
| 2: Non-Linear Regression and Regularization | `assignment-02-regression` | `python run.py` |
| 3: PCA and Model Comparison | `assignment-03-pca` | `python run.py` |
| 4: Insurance Purchase Prediction Web Application | `assignment-04-insurance-api-reference` | See upstream README |
| 5: Single-Layer Perceptron | `assignment-05-perceptron` | `python run.py` |
| 6: MLP for Heart Disease Prediction | `assignment-06-heart-mlp-reference` | See upstream README |
| 7: Random Forest Feature Selection | `assignment-07-feature-selection` | `python run.py` |
| 8: Pneumonia Detection using CNN | `assignment-08-pneumonia-cnn-reference` | See upstream README |
| 9: Real-Time Object Detection using YOLOv8 | `assignment-09-yolov8-webapp-reference` | See upstream README |
| 10: Local LLM Text Summarizer | `assignment-10-summarizer` | `uvicorn app:app --reload` |
| 11: PDF Summarization Agent with Llama 3 | `assignment-11-pdf-summarizer-reference` | See upstream README |
| 12: PDF-Based Retrieval-Augmented Generation Application | `assignment-12-pdf-rag-reference` | See upstream README |

For assignments 2, 3, 5, and 7, install `requirements-ml.txt` in a Python 3.12 environment. Each script writes its measured metrics and plot(s) to its own `results/` directory. Assignments 2 and 3 fetch their UCI datasets on first run.

Assignment 10 has its own `environment.yml` and README. A Conda-compatible environment is available at `.mamba/envs/emea-summarizer`, and `tinyllama` is installed in local Ollama. Ollama must be running when the app generates a summary.

The upstream projects are examples, not original submissions or proof that every assignment requirement was met. See [UPSTREAM.md](UPSTREAM.md) for provenance and assignment gaps.
