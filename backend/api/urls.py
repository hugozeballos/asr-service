from django.urls import path
from .views import TranscribeAPIView

urlpatterns = [
    path("transcribe/", TranscribeAPIView.as_view(), name="transcribe"),
]