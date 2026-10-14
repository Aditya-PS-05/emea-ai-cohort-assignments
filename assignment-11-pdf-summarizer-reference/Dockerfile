FROM python:3.11-slim

WORKDIR /app

# System dependencies - PyMuPDF-ku sila build tools thevai padalam
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Requirements muthalla copy pannitu install pannuvom
# (idha vachu, code maathina mattum, dependencies mீndum download aagathu)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Appuram app code copy pannuvom
COPY app/ ./app/

# uploads folder create pannuvom
RUN mkdir -p uploads

EXPOSE 8000

# --reload production-la venaam - idha remove pannirukom
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]