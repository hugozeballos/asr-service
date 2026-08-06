from django.urls import path, include
from .views import TranscribeAPIView
from .views import AudioUploadView
from .views import ListTranscriptionsView
from rest_framework.routers import DefaultRouter
from .views import UserAdminViewSet

router = DefaultRouter()
router.register(r'users', UserAdminViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path("transcribe/", TranscribeAPIView.as_view(), name="transcribe"),
    path('upload-audio/', AudioUploadView.as_view(), name='upload-audio'),
    path("list-transcriptions/", ListTranscriptionsView.as_view(), name="list_transcriptions"),
]