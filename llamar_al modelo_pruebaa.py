import requests

# URL del modelo desplegado en Cloud Run
url = "https://asr-model-service-463239650270.us-central1.run.app/predict"

# Ruta al archivo de audio que quieres transcribir
audio_path = "C:/Users/User Hugo/Desktop/CNIA/audio_prep_train_180.wav"

with open(audio_path, "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files, timeout=900)

print("Status code:", response.status_code)
print("Response:")
print(response.text)
