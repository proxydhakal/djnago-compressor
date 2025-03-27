from django.urls import path
from .views import  images_to_pdf

urlpatterns = [
    path("images-to-pdf/", images_to_pdf, name="images_to_pdf"),
]