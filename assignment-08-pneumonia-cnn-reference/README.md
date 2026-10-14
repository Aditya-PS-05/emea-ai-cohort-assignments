# Chest X-Ray Pneumonia Classification using CNN

A deep learning project that uses a Convolutional Neural Network (CNN) to classify chest X-ray images into two classes:

- **NORMAL**
- **PNEUMONIA**

The complete implementation is provided in `CNN_PROJECT.ipynb` and is designed to run in a Python/Google Colab environment with GPU support.

## Project Overview

This project builds and evaluates a CNN-based binary image classifier for chest X-ray images. The workflow includes:

1. Installing and importing the required libraries.
2. Downloading the chest X-ray pneumonia dataset using `kagglehub`.
3. Exploring the dataset and its class distribution.
4. Applying image preprocessing and data augmentation.
5. Building an improved CNN architecture.
6. Handling class imbalance with class weights.
7. Training the model for 20 epochs.
8. Plotting training/validation accuracy and loss.
9. Evaluating the trained model on the test dataset.
10. Generating predictions, a confusion matrix, and a classification report.
11. Making predictions on an individual X-ray.
12. Providing an interactive Jupyter/Colab dashboard for selecting an X-ray and viewing its prediction.

## Dataset

The notebook downloads the **Chest X-Ray Images (Pneumonia)** dataset through KaggleHub:

`paultimothymooney/chest-xray-pneumonia`

The dataset is organized into:

```text
chest_xray/
├── train/
├── val/
└── test/
```

The project uses two classes:

```text
NORMAL
PNEUMONIA
```

The training set contains:

- **PNEUMONIA:** 3,875 images
- **NORMAL:** 1,341 images

The notebook also reports:

- **Validation:** 16 images
- **Test:** 624 images

> Dataset counts above are taken directly from the notebook outputs.

## Technologies Used

- Python 3
- TensorFlow / Keras
- NumPy
- Matplotlib
- Seaborn
- Scikit-learn
- Pillow (PIL)
- IPyWidgets
- KaggleHub

## Installation

Install the libraries used by the notebook:

```bash
pip install tensorflow matplotlib seaborn scikit-learn pillow ipywidgets kagglehub
```

The notebook itself installs the main dependencies with:

```bash
pip install tensorflow matplotlib seaborn scikit-learn pillow ipywidgets -q
```

## CNN Architecture

The model accepts RGB images with an input size of **150 × 150 × 3**.

Architecture:

```text
Input: 150 × 150 × 3
        ↓
Conv2D: 32 filters, 3×3, ReLU, same padding
        ↓
Batch Normalization
        ↓
MaxPooling 2×2
        ↓
Conv2D: 64 filters, 3×3, ReLU, same padding
        ↓
Batch Normalization
        ↓
MaxPooling 2×2
        ↓
Conv2D: 128 filters, 3×3, ReLU, same padding
        ↓
Batch Normalization
        ↓
MaxPooling 2×2
        ↓
Conv2D: 256 filters, 3×3, ReLU, same padding
        ↓
Batch Normalization
        ↓
MaxPooling 2×2
        ↓
Global Average Pooling
        ↓
Dense: 128, ReLU
        ↓
Dropout: 0.5
        ↓
Dense: 1, Sigmoid
```

## Image Preprocessing & Data Augmentation

Training images are rescaled using:

```python
rescale=1./255
```

The training pipeline also applies:

- Rotation: up to 8 degrees
- Width shift: 0.05
- Height shift: 0.05
- Zoom: 0.10

Validation and test images are only rescaled by `1./255`.

The images are loaded with:

```python
target_size=IMG_SIZE
batch_size=BATCH_SIZE
class_mode="binary"
```

Training data is shuffled, while test data is not shuffled so that predictions can be compared with the original class labels.

## Class Imbalance Handling

Because the training dataset contains substantially more pneumonia images than normal images, the notebook calculates balanced class weights using Scikit-learn:

```python
compute_class_weight(
    class_weight="balanced",
    classes=np.unique(train_data.classes),
    y=train_data.classes
)
```

The calculated weights in the notebook are approximately:

```text
Class 0: 1.9448
Class 1: 0.6730
```

These weights are passed to `model.fit()` during training.

## Model Compilation

The model uses:

- **Optimizer:** Adam
- **Learning rate:** 0.0001
- **Loss:** Binary Cross-Entropy
- **Metrics:** Accuracy, Precision, Recall

```python
Adam(learning_rate=0.0001)
```

## Training

The model is trained for **20 epochs** using the training and validation datasets.

```python
history = model.fit(
    train_data,
    validation_data=val_data,
    epochs=20,
    class_weight=class_weights
)
```

The notebook also identifies the epoch with the highest validation accuracy.

### Training Observation

The final recorded training epoch shows approximately:

- Training accuracy: **97.34%**
- Training precision: **99.18%**
- Training recall: **97.21%**
- Validation accuracy: **93.75%**
- Validation precision: **100.00%**
- Validation recall: **87.50%**

## Test Results

The notebook evaluates the trained CNN on the test dataset.

Recorded test performance:

| Metric | Result |
|---|---:|
| Test Loss | 0.2929 |
| Test Accuracy | **90.87%** |
| Test Precision | **90.71%** |
| Test Recall | **95.13%** |

These values are the results recorded in the supplied notebook.

## Evaluation

The project evaluates predictions using:

- Accuracy
- Precision
- Recall
- F1-score
- Confusion Matrix
- Classification Report

Predictions are converted into binary classes using a threshold of **0.5**:

```python
predicted_labels = (
    predicted_probabilities >= 0.5
).astype(int).ravel()
```

A confusion matrix is generated with:

```python
confusion_matrix(actual_labels, predicted_labels)
```

The classification report is generated using:

```python
classification_report(
    actual_labels,
    predicted_labels,
    target_names=["NORMAL", "PNEUMONIA"]
)
```

## Single X-Ray Prediction

The notebook can also classify an individual X-ray.

The image is:

1. Loaded and resized to the model input size.
2. Converted to an array.
3. Normalized by dividing pixel values by 255.
4. Expanded to a batch dimension.
5. Passed through the trained CNN.

The model output is interpreted as:

```text
Prediction >= 0.5 → PNEUMONIA
Prediction < 0.5  → NORMAL
```

The notebook displays the predicted class and confidence/probability.

## Interactive Dashboard

The project includes an IPyWidgets-based dashboard titled:

**Chest X-Ray CNN Dashboard — Normal vs Pneumonia Classification**

The dashboard provides:

- A class dropdown (`NORMAL` / `PNEUMONIA`)
- An X-ray image dropdown
- A **Predict** button
- Display of the selected image
- Actual class
- Predicted class
- Prediction confidence

This provides a simple interactive way to test the trained model from inside the notebook.

## How to Run

### Option 1 — Google Colab

1. Open `CNN_PROJECT.ipynb` in Google Colab.
2. Enable GPU runtime if available.
3. Run the notebook cells from top to bottom.
4. Allow KaggleHub to download/access the dataset.
5. Complete training.
6. Review the evaluation metrics and plots.
7. Use the dashboard at the end for interactive predictions.

### Option 2 — Local Jupyter Environment

1. Install Python and the required packages.
2. Open the notebook with Jupyter Notebook or JupyterLab.
3. Ensure the dataset can be downloaded/accessed through KaggleHub.
4. Run the cells sequentially.

## Project Structure

```text
.
├── CNN_PROJECT.ipynb
└── README.md
```

The dataset is downloaded/accessed separately through KaggleHub and is not required to be stored inside the project repository.

## Important Note

This project is an **educational machine-learning project** for image classification. A CNN prediction should not be treated as a medical diagnosis or as a replacement for evaluation by a qualified healthcare professional.

## Future Improvements

Possible extensions include:

- Using transfer learning with architectures such as ResNet, EfficientNet, or MobileNet.
- Increasing and improving validation data.
- Applying stronger regularization and early stopping.
- Performing more systematic hyperparameter tuning.
- Using explainability techniques such as Grad-CAM to visualize image regions influencing predictions.
- Evaluating the model across additional clinical datasets to assess generalization.

## Notebook

Main implementation:

`CNN_PROJECT.ipynb`
