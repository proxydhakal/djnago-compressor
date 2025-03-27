import os
import threading
import shutil
import uuid
import time
import logging
import subprocess
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from .models import FileCompressLog
from PIL import Image  # For image compression
import PyPDF2

# Logging setup
logger = logging.getLogger(__name__)

# Directory paths
INPUT_DIR = os.path.join(settings.MEDIA_ROOT, 'input')
OUTPUT_DIR = os.path.join(settings.MEDIA_ROOT, 'output')

# Ensure directories exist
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Thread lock for safe concurrent writing
thread_lock = threading.Lock()

def generate_compressed_filename(original_filename):
    """
    Generate a unique compressed filename based on input file name.
    """
    name, ext = os.path.splitext(original_filename)
    return original_filename #f"{name}_compressed{ext}"

def is_pdf_encrypted(input_path):
    """
    Check if a PDF file is encrypted.
    """
    try:
        with open(input_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            if reader.is_encrypted:
                return True
    except Exception as e:
        logger.error(f"Error checking PDF encryption: {e}")
    return False

def compress_pdf(input_path, output_path, compression_level):
    """
    Compress a PDF file using Ghostscript.
    """
    if is_pdf_encrypted(input_path):
        logger.error(f"File is encrypted: {input_path}")
        return None  # Return None if the file is encrypted

    try:
        subprocess.run([
            "gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS=/{compression_level}", "-dNOPAUSE", "-dQUIET",
            "-dBATCH", f"-sOutputFile={output_path}", input_path
        ], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Ghostscript compression error: {e}")

def compress_image(input_path, output_path):
    """
    Compress an image file (JPG/PNG) using Pillow.
    """
    try:
        img = Image.open(input_path)
        img.save(output_path, optimize=True, quality=70)
    except Exception as e:
        logger.error(f"Image compression error: {e}")

def compress_file(file, compression_level):
    """
    Compress a single file (PDF or image) and return the output filename.
    """
    input_path = os.path.join(INPUT_DIR, file.name)
    output_filename = generate_compressed_filename(file.name)
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    try:
        # Save uploaded file
        with thread_lock:
            with open(input_path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)
            logger.info(f"File saved: {input_path}")
    except IOError as e:
        logger.error(f"Failed to save {file.name}: {e}")
        return None

    file_extension = file.name.split('.')[-1].lower()
    try:
        if file_extension == 'pdf':
            if is_pdf_encrypted(input_path):
                logger.error(f"PDF file is encrypted: {file.name}")
                return None  # Skip processing for encrypted PDFs
            compress_pdf(input_path, output_path, compression_level)
        elif file_extension in ['jpg', 'jpeg', 'png']:
            compress_image(input_path, output_path)
        else:
            logger.warning(f"Unsupported file type: {file_extension}")
            return None

        # Ensure the file exists before returning
        time.sleep(1)  # Allow file system update
        if not os.path.exists(output_path):
            logger.error(f"File {output_filename} was not created successfully.")
            return None

        with thread_lock:
            original_size = os.path.getsize(input_path)
            compressed_size = os.path.getsize(output_path)
            FileCompressLog.objects.create(
                file_name=file.name,
                original_size=original_size,
                compressed_size=compressed_size,
                file_type=file_extension
            )
            logger.info(f"Compression logged: {file.name} ({original_size} -> {compressed_size} bytes)")

        return output_filename
    except Exception as e:
        logger.error(f"Error compressing {file.name}: {e}")
        return None

def compress_files_concurrently(files, compression_level):
    """
    Compress multiple files concurrently using threads and return output filenames.
    """
    threads = []
    results = []

    def worker(file):
        compressed_filename = compress_file(file, compression_level)
        if compressed_filename:
            with thread_lock:
                results.append(compressed_filename)

    for file in files:
        thread = threading.Thread(target=worker, args=(file,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return results

def upload_and_compress(request):
    """
    Handle file upload and compression for web-based requests.
    """
    if request.method == "POST":
        files = request.FILES.getlist('pdfFiles[]')
        compression_level = request.POST.get('compression_level', 'screen')

        if not files:
            return JsonResponse({"error": "No files provided."}, status=400)

        compressed_filenames = compress_files_concurrently(files, compression_level)

        compressed_files = []
        for filename in compressed_filenames:
            output_path = os.path.join(OUTPUT_DIR, filename)
            if os.path.exists(output_path):
                compressed_files.append(os.path.join(settings.MEDIA_URL, 'output', filename))

        if not compressed_files:
            return JsonResponse({"error": "No files were successfully compressed."}, status=400)

        return JsonResponse({"files": compressed_files}, status=200)

    return render(request, 'public/compress_pdf.html')

class FileUploadCompressAPIView(APIView):
    """
    API view to handle file upload and compression via REST API.
    """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist('files')
        compression_level = request.data.get('compression_level', 'screen')

        if not files:
            return Response({"error": "No files provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            compressed_filenames = compress_files_concurrently(files, compression_level)

            compressed_files = []
            for filename in compressed_filenames:
                output_path = os.path.join(OUTPUT_DIR, filename)
                if os.path.exists(output_path):
                    compressed_files.append(os.path.join(settings.MEDIA_URL, 'output', filename))

            if not compressed_files:
                return Response({"error": "No files were successfully compressed."}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"files": compressed_files}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error during compression: {e}")
            return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




def upload_directory():
    directory = os.path.join(settings.MEDIA_ROOT, "uploads_compressed_images")
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def compress_images(image_file, compression_level):
    try:
        image = Image.open(image_file)
        image = image.convert("RGB")
        quality = int(compression_level)

        original_name = os.path.splitext(image_file.name)[0]  
        compressed_image_name = f"{original_name}_compressed.jpg"
        compressed_image_path = os.path.join(upload_directory(), compressed_image_name)

        image.save(compressed_image_path, "JPEG", quality=quality)

        return compressed_image_name

    except Exception as e:
        return str(e)

def image_compression(request):
    if request.method == "POST" and request.FILES.getlist("image_files"):
        compression_level = request.POST.get("compression_level", 75)
        compression_level = int(compression_level)

        results = []
        invalid_files = []

        for image_file in request.FILES.getlist("image_files"):
            file_extension = image_file.name.split('.')[-1].lower()
            if file_extension not in ['jpg', 'jpeg', 'png', 'webp']:
                invalid_files.append(image_file.name)
                continue

            compressed_filename = compress_images(image_file, compression_level)
            if "Error" in compressed_filename:
                invalid_files.append(image_file.name)
            else:
                results.append({
                    "original_name": image_file.name,
                    "original_url": os.path.join(settings.MEDIA_URL, "uploads_compressed_images", image_file.name),
                    "compressed_name": compressed_filename,
                    "compressed_url": os.path.join(settings.MEDIA_URL, "uploads_compressed_images", compressed_filename),
                })

        return JsonResponse({
            "results": results,
            "invalid_files": invalid_files,
        })

    return render(request, "public/image_compression.html")