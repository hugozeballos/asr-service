import os
import requests
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status

# URL del microservicio del modelo (puedes definirla como variable de entorno en producción)
MODEL_SERVICE_URL = os.environ.get("MODEL_SERVICE_URL", "http://asr-model-service:8000")

class TranscribeAPIView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        audio_file = request.FILES.get("audio")
        if not audio_file:
            return Response({"error": "Se requiere un archivo 'audio'"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Enviamos el archivo al microservicio del modelo
            response = requests.post(
                f"{MODEL_SERVICE_URL}/predict",
                files={"file": audio_file},
                
                timeout=60  # puedes ajustar este valor según necesidad
            )
            response.raise_for_status()
            return Response(response.json())

        except requests.RequestException as e:
            return Response({"error": "Error al contactar al microservicio del modelo", "details": str(e)},
                            status=status.HTTP_502_BAD_GATEWAY)