import requests

# URL del backend desplegado en Cloud Run
backend_url = "https://asr-backend-service-463239650270.us-central1.run.app/api/transcribe/"

# Ruta local del audio
audio_path = "C:/Users/User Hugo/Desktop/CNIA/audio_prep_train_180.wav"

# Enviar audio al backend
with open(audio_path, "rb") as f:
    files = {"file": f}
    try:
        response = requests.post(backend_url, files=files, timeout=600)
        print("Status code:", response.status_code)

        try:
            print("JSON response:", response.json())  # si es JSON
        except ValueError:
            print("Text response:", response.text)    # si es texto plano

    except requests.exceptions.RequestException as e:
        print("❌ Error al conectar con el backend:", e)
