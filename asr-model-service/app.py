from fastapi import FastAPI, UploadFile, File
from transformers import pipeline
import torch

app = FastAPI()

# Carga del modelo (una vez)
pipe = pipeline("automatic-speech-recognition", model="facebook/mms-1b-all")

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    result = pipe(audio_bytes)
    return {"text": result['text']}
