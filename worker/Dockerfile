FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg libsndfile1 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY worker/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY worker/separate.py ./separate.py
CMD ["sh", "-c", "uvicorn separate:app --host 0.0.0.0 --port ${PORT:-8000}"]
