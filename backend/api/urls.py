from django.urls import path
from .views import TranscribeAPIView
from .views import AudioUploadView

urlpatterns = [
    path("transcribe/", TranscribeAPIView.as_view(), name="transcribe"),
    path('upload-audio/', AudioUploadView.as_view(), name='upload-audio'),
]