import os
import requests
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from .gcp_clients import upload_audio_to_gcs, save_metadata_to_firestore

class AudioUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('audio')
        transcription = request.data.get('transcription')
        corrected = request.data.get('corrected_transcription', None)

        if not file or not transcription:
            return Response({'error': 'Missing audio file or transcription'}, status=400)

        filename = file.name
        user_id = request.user.id

        try:
            audio_url = upload_audio_to_gcs(file, filename)
            save_metadata_to_firestore(user_id, filename, transcription, corrected)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

        return Response({'message': 'Upload successful', 'file_url': audio_url})



class TranscribeAPIView(APIView):
    permission_classes = [IsAuthenticated]
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