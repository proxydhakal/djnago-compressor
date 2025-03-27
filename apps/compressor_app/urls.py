# compressor_app/urls.py
from django.urls import path
from apps.compressor_app.views import upload_and_compress, FileUploadCompressAPIView, image_compression
from rest_framework.documentation import include_docs_urls
from rest_framework import routers
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
# Define schema view for Swagger docs
schema_view = get_schema_view(
    openapi.Info(
        title="File Compression API",
        default_version='v1',
        description="API to upload and compress files",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@myapi.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
)


urlpatterns = [
    path('compress/pdf/', upload_and_compress, name='upload_and_compress'),
    path('compress/image/', image_compression, name='image_compression'),
    path('api/compress/', FileUploadCompressAPIView.as_view(), name='file-upload-compress'),
    path('api/documentation/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
]
