# compressor_app/urls.py
from django.urls import path
from apps.compressor_app.views import upload_and_compress, FileUploadCompressAPIView, home
from rest_framework.documentation import include_docs_urls
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
# Define schema view for Swagger docs
schema_view = get_schema_view(
   openapi.Info(
      title="File Compression API",
      default_version='v1',
      description="API for uploading and compressing files",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="your-email@example.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
)

urlpatterns = [
    path('', home, name='home'),
    path('compress/pdf/', upload_and_compress, name='upload_and_compress'),
    path('api/compress/', FileUploadCompressAPIView.as_view(), name='file-upload-compress'),
    path('api/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-docs'),

]
