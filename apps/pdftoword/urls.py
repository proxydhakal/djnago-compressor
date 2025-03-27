from django.urls import path
from .views import pdf_to_word, pdf_to_word_page

urlpatterns = [
    path("pdf-to-word/", pdf_to_word_page, name="pdf_to_word_page"),
    path("convert-pdf-to-word/", pdf_to_word, name="pdf_to_word"),
]
