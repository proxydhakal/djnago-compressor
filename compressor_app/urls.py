# compressor_app/urls.py
from django.urls import path
from .views import upload_and_compress

urlpatterns = [
    path('', upload_and_compress, name='upload_and_compress'),
]
