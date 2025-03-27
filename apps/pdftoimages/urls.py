from django.urls import path
from .views import pdf_to_images
urlpatterns = [
    path("pdf-to-images/", pdf_to_images, name="pdf_to_images"),
]