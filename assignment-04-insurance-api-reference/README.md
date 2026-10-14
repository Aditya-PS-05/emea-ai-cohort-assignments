# 🏥 Insurance Premium Prediction API

> A Machine Learning-powered web application built with **FastAPI** that predicts insurance premiums based on user information.

<p align="center">
    <img src="https://img.shields.io/badge/Python-3.10+-blue.svg">
    <img src="https://img.shields.io/badge/FastAPI-Framework-green.svg">
    <img src="https://img.shields.io/badge/Scikit--Learn-Machine%20Learning-orange.svg">
    <img src="https://img.shields.io/badge/Status-Completed-success.svg">
</p>

---

# 📖 About

This project demonstrates how to deploy a Machine Learning model using **FastAPI**.

Users enter their details such as age, BMI, smoking habits, number of children, and region, and the application predicts the expected insurance premium using a trained regression model.

The project follows a clean folder structure by separating API routes, ML model, schemas, and configuration files.

---

# ✨ Features

- 🚀 FastAPI REST API
- 🤖 Machine Learning Prediction
- 📊 Insurance Premium Estimation
- ✅ Pydantic Request Validation
- 📄 Automatic Swagger Documentation
- 🎨 Simple Frontend Interface
- 📦 Modular Project Structure

---

# 🛠 Tech Stack

- Python
- FastAPI
- Scikit-Learn
- Pandas
- NumPy
- Pydantic
- Uvicorn
- HTML/CSS (Frontend)

---

# 📂 Project Structure

```text
insurance-premium-prediction-fastapi/
│
├── config/
│   └── city_tear.py
│
├── model/
│   ├── model.pkl
│   └── predict.py
│
├── schema/
│   ├── user_input.py
│   └── prediction_response.py
│
├── Fastapi_ml_model.ipynb
├── app.py
├── frontend.py
│
└── README.md
```

---

# ⚙️ Workflow

```text
User Input
      │
      ▼
Frontend / FastAPI
      │
      ▼
Pydantic Validation
      │
      ▼
Prediction Pipeline
      │
      ▼
Machine Learning Model
      │
      ▼
Predicted Insurance Premium
```

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/ShrutiPatel263/insurance-premium-prediction-fastapi.git
```

Navigate to the project

```bash
cd insurance-premium-prediction-fastapi
```

Create virtual environment

```bash
python -m venv venv
```

Activate virtual environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Run the API

```bash
uvicorn app:app --reload
```

Application will start at

```
http://127.0.0.1:8000
```

---

# 📖 API Documentation

FastAPI automatically provides interactive API documentation.

### Swagger UI

```
http://127.0.0.1:8000/docs
```

### ReDoc

```
http://127.0.0.1:8000/redoc
```

---

# 🧠 Machine Learning Pipeline

The model predicts insurance premiums using features such as:

- Age
- Gender
- BMI
- Number of Children
- Smoking Status
- Region
- City Tier

The trained model is stored as a serialized `.pkl` file and loaded during API execution.

---

# 📁 Modules

### 📌 config

Contains configuration-related utilities.

### 📌 model

Loads the trained Machine Learning model and performs predictions.

### 📌 schema

Defines request and response models using **Pydantic**.

### 📌 frontend.py

Provides a simple user interface to interact with the prediction API.

### 📌 Fastapi_ml_model.ipynb

Notebook used for data preprocessing, model training, evaluation, and exporting the trained model.

---

# 🎯 Learning Outcomes

Through this project, I learned:

- Building REST APIs with FastAPI
- Deploying Machine Learning models
- Structuring scalable FastAPI applications
- Pydantic Data Validation
- API Documentation using Swagger
- Model Serialization using Pickle
- Connecting Machine Learning with Backend Development

---

<p align="center">
Made with ❤️ using FastAPI & Machine Learning
</p>
