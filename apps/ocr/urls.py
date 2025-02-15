from django.urls import path
from .views import ocr_upload

urlpatterns = [
    path('ocr/', ocr_upload, name='ocr_upload'),
]
