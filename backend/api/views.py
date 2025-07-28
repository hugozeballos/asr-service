import os
import requests
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings


class TranscribeAPIView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        
        audio_file = request.FILES.get("file")
        if not audio_file:
            return Response({"error": "Se requiere un archivo 'audio'"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            print("📡 Enviando solicitud al modelo:", settings.ASR_MODEL_URL)
            print("📎 Nombre del archivo:", audio_file.name)
            print("📏 Tamaño:", audio_file.size)
            # Enviamos el archivo al microservicio del modelo
            response = requests.post(
                settings.ASR_MODEL_URL,
                files={"file": audio_file},
                
                timeout=900  # puedes ajustar este valor según necesidad
            )
            response.raise_for_status()
            print(f"🟢 Status del modelo: {response.status_code}")
            print(f"🟢 Texto de respuesta (parcial): {response.text[:300]}")
            try:
                return Response(response.json())
            except ValueError:
                return Response({"text": response.text})

        except requests.RequestException as e:
            print("❌ Error al enviar solicitud al modelo:", e)
            return Response({"error": "Error al contactar al microservicio del modelo", "details": str(e)},
                            status=status.HTTP_502_BAD_GATEWAY)