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
from django.contrib.auth.models import User
from rest_framework import serializers


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


class IsAdmin(permissions.BasePermission):
    """Restricts a view to authenticated users with is_staff=True."""

    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class UserAdminViewSet(viewsets.ModelViewSet):
    """Staff-only CRUD over Django users, used by the /admin_usuarios frontend page."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]


class ListTranscriptionsView(APIView):
    """Returns every saved transcription/correction pair from Firestore.

    Not filtered by user_id yet: any authenticated user currently sees all
    transcriptions, not just their own.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        db = firestore.Client()
        docs = db.collection("audios").stream()

        result = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            result.append(data)
        return Response(result)

class AudioUploadView(APIView):
    """Uploads an audio file to GCS and stores its transcription/correction in Firestore."""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('audio')
        transcription = request.data.get('transcription')
        corrected = request.data.get('corrected_transcription', None)

        if not file or not transcription:
            return Response({'error': 'Missing audio file or transcription'}, status=400)

        # Generate the storage filename instead of trusting the client-supplied
        # one, to avoid collisions/overwrites and path-traversal-style names.
        import uuid, os
        ext = os.path.splitext(file.name)[1] or ".webm"
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
    """Forwards an uploaded audio file to the ASR model microservice and relays its response."""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        audio_file = request.FILES.get("file")
        if not audio_file:
            return Response({"error": "Se requiere un archivo 'audio'"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = requests.post(
                settings.ASR_MODEL_URL,
                files={"file": audio_file},
                timeout=900,  # the model service can be slow on cold start / long audio
            )
            response.raise_for_status()
            try:
                return Response(response.json())
            except ValueError:
                return Response({"text": response.text})

        except requests.RequestException as e:
            return Response({"error": "Error al contactar al microservicio del modelo", "details": str(e)},
                            status=status.HTTP_502_BAD_GATEWAY)