from django.urls import path
from .views import VideoCompressionView, CheckTaskStatus, GetCompressedVideo

urlpatterns = [
    path("compress/video/", VideoCompressionView.as_view(), name="compress_video"),
    path("compress/video/check_status/<str:task_id>/", CheckTaskStatus.as_view(), name="check_video_status"),
    path("compress/get_video/<str:task_id>/", GetCompressedVideo.as_view(), name="get_video"),
]
