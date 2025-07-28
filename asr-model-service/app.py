from fastapi import FastAPI, UploadFile, File
from transformers import Wav2Vec2ForCTC, AutoTokenizer, AutoFeatureExtractor, pipeline
import torch
import io
import soundfile as sf
from pydub import AudioSegment
import magic
import mimetypes

app = FastAPI()

# Carga explícita del modelo y assets desde cache local
model = Wav2Vec2ForCTC.from_pretrained("facebook/mms-1b-all", local_files_only=True, torch_dtype=torch.float16)
tokenizer = AutoTokenizer.from_pretrained("facebook/mms-1b-all", local_files_only=True)
feature_extractor = AutoFeatureExtractor.from_pretrained('facebook/mms-1b-all', local_files_only=True)

# Carga del modelo (una vez)
pipe = pipeline("automatic-speech-recognition", model=model, tokenizer=tokenizer, feature_extractor=feature_extractor, framework="pt")

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    audio_bytes = await file.read()

    # Detectar tipo MIME
    mime = magic.Magic(mime=True)
    with open("temp_input", "wb") as temp_file:
        temp_file.write(audio_bytes)
    mime_type = mime.from_file("temp_input")

    # Convertir si es necesario
    wav_io = io.BytesIO()
    if "webm" in mime_type:
        print("🔄 Convirtiendo de WEBM a WAV...")
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="webm")
        audio.export(wav_io, format="wav")
        wav_io.seek(0)
    elif "mp3" in mime_type:
        print("🔄 Convirtiendo de MP3 a WAV...")
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
        audio.export(wav_io, format="wav")
        wav_io.seek(0)
    else:
        print("✅ Formato compatible o desconocido, usando directamente")
        wav_io = io.BytesIO(audio_bytes)

    # Leer audio y hacer inferencia
    audio_input, sample_rate = sf.read(wav_io)

    result = pipe({
        "array": audio_input,
        "sampling_rate": sample_rate
    })
    return {"text": result['text']}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080)