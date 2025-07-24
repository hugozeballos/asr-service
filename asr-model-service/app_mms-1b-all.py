from fastapi import FastAPI, UploadFile, File
from transformers import Wav2Vec2ForCTC, AutoTokenizer, AutoFeatureExtractor, pipeline
import torch
import io
import soundfile as sf

app = FastAPI()

# Carga explícita del modelo y assets desde cache local
model = Wav2Vec2ForCTC.from_pretrained("facebook/mms-1b-all", local_files_only=True, torch_dtype=torch.float16)
tokenizer = AutoTokenizer.from_pretrained("facebook/mms-1b-all", local_files_only=True)
feature_extractor = AutoFeatureExtractor.from_pretrained("facebook/mms-1b-all", local_files_only=True)

# Carga del modelo (una vez)
pipe = pipeline("automatic-speech-recognition", model=model, tokenizer=tokenizer, feature_extractor=feature_extractor, framework="pt")

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    # Decode audio file from bytes (e.g. .wav or .flac)
    audio_input, sample_rate = sf.read(io.BytesIO(audio_bytes))
    result = pipe({
        "array": audio_input,
        "sampling_rate": sample_rate
    })
    return {"text": result['text']}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080)