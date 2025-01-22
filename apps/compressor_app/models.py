# compressor_app/models.py
from django.db import models

class UploadedFile(models.Model):
    file = models.FileField(upload_to='input/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class FileCompressLog(models.Model):
    id = models.BigAutoField(primary_key=True)  # Primary key
    file_name = models.CharField(max_length=255)  # Name of the file
    original_size = models.BigIntegerField()  # Size before compression (in bytes)
    compressed_size = models.BigIntegerField()  # Size after compression (in bytes)
    file_type = models.CharField(max_length=50)  # File type (e.g., .zip, .jpg, etc.)
    compressed_at = models.DateTimeField(auto_now_add=True)  # Timestamp of compression

    def __str__(self):
        return f"{self.file_name} ({self.file_type})"

    class Meta:
        verbose_name = "File Compression Log"
        verbose_name_plural = "File Compression Logs"
        ordering = ['-compressed_at']
