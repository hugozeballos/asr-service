from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import requests

class TranscribeView(APIView):
    def post(self, request):
        audio_file = request.FILES.get('file')
        if not audio_file:
            return Response({"error": "No audio file provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # URL configurable desde settings
            model_url = settings.ASR_MODEL_URL

            files = {'file': (audio_file.name, audio_file.read(), audio_file.content_type)}
            response = requests.post(model_url, files=files)

            if response.status_code == 200:
                return Response(response.json(), status=200)
            else:
                return Response({
                    "error": "Error calling model service",
                    "details": response.text
                }, status=response.status_code)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
