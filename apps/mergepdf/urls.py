from django.urls import path
from . import views

urlpatterns = [
    path('merge-pdfs/', views.merge_pdfs_view, name='merge_pdfs'),
]
