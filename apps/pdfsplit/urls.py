from django.urls import path
from . import views

urlpatterns = [
    path('upload/pdf/split/', views.upload_pdf, name='upload_pdf_split'),
    path('split/', views.split_pdf, name='split_pdf'),
]
