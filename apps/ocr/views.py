import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import render

# Set Tesseract path (only required on Windows)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image_path):
    """ Extract text from an image using Tesseract OCR """
    return pytesseract.image_to_string(Image.open(image_path))

def extract_text_from_pdf(pdf_path):
    """ Convert PDF pages to images and extract text """
    images = convert_from_path(pdf_path)
    extracted_text = ""
    
    for image in images:
        extracted_text += pytesseract.image_to_string(image) + "\n"
    
    return extracted_text

def ocr_upload(request):
    """ Handles OCR file uploads and text extraction via AJAX """
    if request.method == "POST" and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        file_name = uploaded_file.name.lower()
        
        # Save uploaded file temporarily
        file_path = default_storage.save(f"ocr_uploads/{file_name}", ContentFile(uploaded_file.read()))
        full_file_path = default_storage.path(file_path)

        # Extract text based on file type
        extracted_text = ""
        if file_name.endswith(('.png', '.jpg', '.jpeg', '.tiff')):
            extracted_text = extract_text_from_image(full_file_path)
        elif file_name.endswith('.pdf'):
            extracted_text = extract_text_from_pdf(full_file_path)
        else:
            return JsonResponse({"error": "Unsupported file format!"}, status=400)

        return JsonResponse({"text": extracted_text})

    return render(request, 'public/ocr_upload.html')
