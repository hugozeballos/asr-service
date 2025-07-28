FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HF_HUB_DISABLE_SYMLINKS_WARNING=1
# Crear carpeta para cache local de modelos
ENV TRANSFORMERS_CACHE=/app/cache

WORKDIR /app

# Instala dependencias del sistema
RUN apt-get update && apt-get install -y libsndfile1 ffmpeg libmagic1 sox libsox-dev && rm -rf /var/lib/apt/lists/*

# Copia e instala dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Crea carpeta y descarga modelo/tokenizer/extractor localmente

RUN python -c "from transformers import Wav2Vec2ForCTC, AutoTokenizer, AutoFeatureExtractor; Wav2Vec2ForCTC.from_pretrained('facebook/mms-1b-all'); AutoTokenizer.from_pretrained('facebook/mms-1b-all'); AutoFeatureExtractor.from_pretrained('facebook/mms-1b-all')"



# Copia tu aplicación
COPY app.py .

EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]