# compressor_app/models.py
from django.db import models

class UploadedFile(models.Model):
    file = models.FileField(upload_to='input/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
