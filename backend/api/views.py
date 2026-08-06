import os
import requests
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from .gcp_clients import upload_audio_to_gcs, save_metadata_to_firestore
from google.cloud import firestore

from rest_framework import viewsets, permissions
from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User
from rest_framework import serializers

# Serializador
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_active', 'password']
        extra_kwargs = {
            'is_staff': {'required': True},
            'is_active': {'required': True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            is_staff=validated_data.get('is_staff', False),
            is_active=validated_data.get('is_active', True)
        )
        return user

# Permiso personalizado (solo admin)
class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

# Vista
class UserAdminViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

class ListTranscriptionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        db = firestore.Client()
        collection_ref = db.collection("audios")
        docs = collection_ref.stream()

        user_id = str(request.user.id)
        print("👤 Solicitando transcripciones para user_id:", user_id)

        result = []
        for doc in docs:
            data = doc.to_dict()
            print("📄 Documento Firestore:", data)  # 👈 agrega esto
            data["id"] = doc.id
            result.append(data)
        print("📦 Total filtrado:", len(result))
        return Response(result)

class AudioUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('audio')
        transcription = request.data.get('transcription')
        corrected = request.data.get('corrected_transcription', None)

        if not file or not transcription:
            return Response({'error': 'Missing audio file or transcription'}, status=400)

        import uuid, os
        ext = os.path.splitext(file.name)[1] or ".webm"  # por si viene sin extensión
        filename = f"audio_{uuid.uuid4().hex}{ext}"
        user_id = str(request.user.id)

        try:
            audio_url = upload_audio_to_gcs(file, filename)
            data = {
                "user_id": user_id,
                "filename": filename,
                "audio_url": audio_url,
                "transcription": transcription,
                "corrected": corrected,
            }
            save_metadata_to_firestore(data)
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