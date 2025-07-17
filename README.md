# ASR Service PoC

**Objetivo:**  
- Frontend en Next.js para subir y reproducir audio y mostrar la transcripción.  
- Backend en Django + DRF que llame al modelo `mdmev/whisper-small-hi`.  
- Ambos servicios en Docker y desplegados en Cloud Run.

**Estructura inicial**  
- /frontend    → Next.js  
- /backend     → Django + DRF

This repository contains a minimal proof of concept for an automatic speech recognition service.

## Components

- **Frontend** – A Next.js application that allows uploading an audio file and displays the transcription.
- **Backend** – A Django REST Framework API exposing `/api/transcribe/` which uses the Hugging Face model `mdmev/whisper-small-hi` to transcribe audio.

Both services include Dockerfiles so they can be built independently or via `docker-compose`.

## Local development

1. Install dependencies for the backend:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. Install dependencies for the frontend:
   ```bash
   cd frontend && npm install
   ```
3. Run the backend:
   ```bash
   python manage.py runserver
   ```
4. In another terminal run the frontend:
   ```bash
   npm run dev
   ```
5. Open `http://localhost:3000` in your browser. Upload an audio file and you should receive the transcription.

Alternatively you can build the containers with Docker:

```bash
docker compose up --build