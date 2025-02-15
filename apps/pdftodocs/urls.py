from django.urls import path
from .views import upload_and_convert

urlpatterns = [
    path('convert/docxtopdf/', upload_and_convert, name='upload_and_convert'),
]
