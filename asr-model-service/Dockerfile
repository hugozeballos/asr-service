FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TRANSFORMERS_CACHE=/app/cache

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 🔽 Descarga el modelo durante el build
RUN python -c "\
from transformers import pipeline; \
pipeline('automatic-speech-recognition', model='facebook/mms-1b-all')"

COPY app.py .

EXPOSE 8080
CMD ["python", "app.py"]