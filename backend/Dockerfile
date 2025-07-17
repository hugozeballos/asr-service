# 1. Imagen base Python ligera
FROM python:3.11-slim
RUN pip install --upgrade pip

# 2. Dependencias del SO (para soundfile, librosa…)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 3. Copiar e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar el código
COPY . .

# 5. Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=core.settings \
    PORT=8080

# 6. Puerto en el que escucha Cloud Run
EXPOSE 8080

# 7. Arranque con Gunicorn (ASGI en producción)
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8080"]
