# ASR Service

A proof-of-concept automatic speech recognition (ASR) system composed of three services: a **Next.js** frontend for recording/uploading audio, a **Django REST Framework** backend that handles auth and orchestration, and a **FastAPI** microservice that runs a Hugging Face speech-to-text model. A user records or uploads an audio clip, the audio is transcribed to text, and the transcription can be reviewed, corrected, and saved back to cloud storage for later use (e.g. dataset building or fine-tuning).

> **Project context:** this repository was built during a contract at [CENIA](https://cenia.cl) (Centro Nacional de Inteligencia Artificial, Chile's national AI research center) as part of a larger effort to build an AI-powered Rapa Nui language translator. The code itself is a general-purpose ASR pipeline; no Rapa Nui-specific language configuration, dataset, or model adapter is currently present in this repo (see "Open questions" below).
>
> It's a sibling repo to [`translator-debug`](https://github.com/hugozeballos/translator-debug), the main translator application. That app's own `/api/asr/transcribe/` endpoint currently returns a mocked transcript (`provider: "mock"`); `asr-service` is the standalone, real speech-to-text implementation intended to back it.

## Tech Stack

**Frontend** (`frontend/`)
- Next.js 15 (React 19, TypeScript)
- Tailwind CSS
- Records audio via the browser `MediaRecorder` API or accepts a file upload, plays it back, and calls the backend to transcribe and (optionally) save corrections
- Deployed as a Docker container (Node 18 Alpine, multi-stage build)

**Backend** (`backend/`)
- Django 5.2 + Django REST Framework
- JWT authentication (`djangorestframework-simplejwt`) — all API endpoints require an authenticated user
- `django-cors-headers` for CORS
- PostgreSQL via Cloud SQL
- Google Cloud Storage (audio files) and Firestore (transcription/correction metadata) via `google-cloud-storage` / `google-cloud-firestore`
- Served with Gunicorn in production
- Acts as a thin proxy/orchestrator — it does not run the model itself; it forwards audio to the ASR model microservice over HTTP

**ASR model service** (`asr-model-service/`)
- FastAPI + Uvicorn
- Hugging Face `transformers` pipeline running **`facebook/mms-1b-all`** — Meta's Massively Multilingual Speech (MMS) model, a `Wav2Vec2ForCTC` checkpoint (not Whisper)
- PyTorch, `soundfile` / `torchaudio` for audio decoding; the active `app.py` also uses `pydub` + `python-magic` to detect and convert WebM/MP3 uploads to WAV before inference
- GPU-accelerated: the Dockerfile is based on `nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04` and the model/pipeline is loaded onto `device=0`
- An alternate, simpler variant (`app_mms-1b-all.py`, with a CPU-only `Dockerfile_mms-1b-all.txt`) is kept in the repo but is not the one actually built (the build `Dockerfile` copies `app.py`)

**Infrastructure**
- Each service has its own Dockerfile and is deployed independently to **Google Cloud Run** (project `asr-service-poc`), built via Google Cloud Build
- `service-gpu.yaml` is a Cloud Run/Knative service spec that requests an NVIDIA L4 GPU for the model service
- `codigos.txt` contains the `gcloud builds submit` / `gcloud run deploy` commands used to build and deploy each of the three services

## API

Exposed by the Django backend (JWT-protected unless noted):

| Endpoint | Method | Description |
|---|---|---|
| `/api/token/` | POST | Obtain a JWT access/refresh token pair (username + password) |
| `/api/token/refresh/` | POST | Refresh an access token |
| `/api/transcribe/` | POST (multipart, field `file`) | Forwards the audio file to the ASR model service and returns its JSON response (`{"text": ...}`) |
| `/api/upload-audio/` | POST (multipart, fields `audio`, `transcription`, optional `corrected_transcription`) | Uploads the audio to a GCS bucket and stores the transcription/correction pair in Firestore |

The model microservice itself exposes a single endpoint:

| Endpoint | Method | Description |
|---|---|---|
| `/predict` | POST (multipart, field `file`) | Runs the audio through the `facebook/mms-1b-all` ASR pipeline and returns `{"text": ...}` |

## How it fits into the pipeline

1. The frontend (`/grabar` page) records or accepts an audio upload and posts it to the backend's `/api/transcribe/`.
2. The backend forwards the raw audio to the model microservice's `/predict` endpoint (URL configured via `ASR_MODEL_URL`) and relays the transcription back to the frontend.
3. The user can accept the transcription or edit it in the UI; either way it can be submitted to `/api/upload-audio/`, which stores the audio in Cloud Storage and the original + corrected text in Firestore.

This repo only performs **speech-to-text**; it does not call any translation API itself. Given the project context, it's reasonable to infer this ASR service is meant to sit upstream of a separate translation component that consumes its transcribed text — but no such integration (API call, shared contract, or reference) exists in this codebase, so that connection could not be confirmed from the code.

## Running locally

Each service can be run independently.

**Backend**
```bash
pip install -r backend/requirements.txt
# Required/relevant env vars (see backend/core/settings.py):
#   DB_NAME, DB_USER, DB_PASSWORD, DB_HOST  (PostgreSQL connection)
#   ASR_MODEL_URL   (defaults to http://localhost:8081/predict)
#   GCS_BUCKET_NAME (bucket used by /api/upload-audio/)
python backend/manage.py runserver
```

**Frontend**
```bash
cd frontend
npm install
# NEXT_PUBLIC_API_BASE_URL must point to the backend, e.g. http://localhost:8000
npm run dev
```

**ASR model service**
```bash
cd asr-model-service
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8080
```
Note: `app.py` loads `facebook/mms-1b-all` with `device=0`, i.e. it expects a CUDA GPU to be available.

Each service also has a Dockerfile for containerized builds (`docker build` from within `frontend/`, `backend/`, and `asr-model-service/` respectively); there is no `docker-compose.yml` in this repo, so services are built/deployed individually (see `codigos.txt` for the Cloud Build/Cloud Run commands used in this project).

## Open questions / not confirmed in code

- **Language target**: `facebook/mms-1b-all` supports 1000+ languages via per-language adapters, but the code does not call `load_adapter()` or set a target language anywhere — it loads the base checkpoint as-is. No reference to Rapa Nui (or its ISO code `rap`) appears in the codebase.
- **Link to a translation service**: no code, config, or comment in *this* repo references a separate translation service or API contract with one — the connection is established from the other side, via `translator-debug`'s README (see "Project context" above).
- Two versions of the model service exist (`app.py`, GPU/webm-aware, actively built; `app_mms-1b-all.py`, CPU, unused by the Dockerfile) — kept here as-is rather than guessing which was the intended final version.
