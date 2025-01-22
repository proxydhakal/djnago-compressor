import os
import shutil
import threading
import logging
import subprocess
from PIL import Image
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.conf import settings
from PyPDF2 import PdfReader
from apps.compressor_app.models import FileCompressLog

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define input and output directories
INPUT_DIR = os.path.join(settings.MEDIA_ROOT, 'input')
OUTPUT_DIR = os.path.join(settings.MEDIA_ROOT, 'output')

# Ensure directories exist
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Lock for thread-safe database operations
db_lock = threading.Lock()


def generate_compressed_filename(original_filename):
    """
    Return the original filename without any modifications.
    """
    return original_filename


def determine_compression_level(input_pdf):
    """
    Determine the appropriate compression level based on the content of the PDF.
    """
    try:
        reader = PdfReader(input_pdf)
        has_text = False
        has_images = False

        for page in reader.pages:
            text = page.extract_text()
            if text:
                has_text = True
            # Check for images (if any)
            if '/XObject' in page.get('/Resources', {}):
                has_images = True

            if has_text and has_images:
                break

        if has_text and not has_images:
            return "screen"  # Soft copy
        elif has_images:
            return "ebook"  # Scanned copy
        else:
            return "screen"  # Default to screen if no text or images found

    except Exception as e:
        logger.error(f"Error determining compression level for {input_pdf}: {e}")
        return "screen"  # Default to screen on error


def compress_pdf(input_pdf, output_pdf):
    """
    Compress a single PDF using Ghostscript.
    """
    compression_level = determine_compression_level(input_pdf)
    gs_command = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS=/{compression_level}",
        "-dNOPAUSE",
        "-dBATCH",
        f"-sOutputFile={output_pdf}",
        input_pdf,
    ]
    try:
        subprocess.run(gs_command, check=True)
        logger.info(f"Compressed {input_pdf} to {output_pdf}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error compressing {input_pdf}: {e}")


def compress_image(input_image, output_image):
    """
    Compress an image (JPEG/PNG) without changing DPI or pixel dimensions.
    """
    try:
        with Image.open(input_image) as img:
            img.save(output_image, quality=50, optimize=True)
            logger.info(f"Compressed image {input_image} to {output_image}")
    except Exception as e:
        logger.error(f"Error compressing image {input_image}: {e}")


def is_file_corrupted(file_path):
    """
    Check if a file is corrupted or contains unsupported metadata.
    """
    try:
        file_extension = file_path.split('.')[-1].lower()

        if file_extension == 'pdf':
            # Attempt to read the PDF file
            PdfReader(file_path)
        elif file_extension in ['jpg', 'jpeg', 'png']:
            # Attempt to open the image
            with Image.open(file_path) as img:
                img.verify()
        else:
            logger.warning(f"Unsupported file type: {file_extension}")
            return True

        return False  # File is valid
    except Exception as e:
        logger.error(f"File corruption/unsupported metadata detected in {file_path}: {e}")
        return True  # File is corrupted


def compress_files_concurrently(file_paths):
    """
    Compress multiple files concurrently using threads and log the results.
    """
    threads = []
    output_files = []

    def log_compression(file_path, output_path, original_size, compressed_size, file_type):
        """
        Log the compression details into FileCompressLog model.
        """
        try:
            with db_lock:  # Ensure thread-safe DB operations
                FileCompressLog.objects.create(
                    file_name=os.path.basename(file_path),
                    original_size=original_size,
                    compressed_size=compressed_size,
                    file_type=file_type,
                    compressed_at=datetime.now()
                )
                logger.info(f"Logged compression for {file_path}")
        except Exception as e:
            logger.error(f"Error logging compression for {file_path}: {e}")

    for file_path in file_paths:
        if is_file_corrupted(file_path):
            logger.warning(f"Skipping corrupted or unsupported file: {file_path}")
            continue

        output_filename = generate_compressed_filename(os.path.basename(file_path))
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        # Determine file extension and choose the appropriate compression method
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == '.pdf':
            thread = threading.Thread(
                target=lambda: (
                    compress_pdf(file_path, output_path),
                    log_compression(
                        file_path,
                        output_path,
                        os.path.getsize(file_path),
                        os.path.getsize(output_path) if os.path.exists(output_path) else 0,
                        "PDF"
                    )
                )
            )
        elif file_extension in ['.jpg', '.jpeg', '.png']:
            thread = threading.Thread(
                target=lambda: (
                    compress_image(file_path, output_path),
                    log_compression(
                        file_path,
                        output_path,
                        os.path.getsize(file_path),
                        os.path.getsize(output_path) if os.path.exists(output_path) else 0,
                        "Image"
                    )
                )
            )
        else:
            logger.warning(f"Unsupported file type: {file_extension}")
            continue

        threads.append(thread)
        output_files.append(output_path)

    # Start and join threads
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()  # Ensure each thread completes before moving forward

    return output_files



def upload_and_compress(request):
    """
    Handle file upload and compression.
    """
    if request.method == "POST":
        files = request.FILES.getlist('pdfFiles[]')

        uploaded_files = []
        for file in files:
            file_path = os.path.join(INPUT_DIR, generate_compressed_filename(file.name))
            with open(file_path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)
            uploaded_files.append(file_path)

        try:
            output_files = compress_files_concurrently(uploaded_files)
            compressed_files = [
                os.path.join(settings.MEDIA_URL, 'output', os.path.basename(f))
                for f in output_files
            ]
            return JsonResponse({"files": compressed_files}, status=200)
        except Exception as e:
            logger.error(f"Error during compression: {e}")
            return JsonResponse({"error": "Internal server error."}, status=500)

    return render(request, 'public/compress_pdf.html')

from apps.compressor_app.serializers import FileUploadSerializer
class FileUploadCompressAPIView(APIView):
    """
    API view to handle file upload and compression.
    """

    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        request_body=None,  # Disable automatic schema generation for the body
        manual_parameters=[  # Manually define the file fields as formData
            openapi.Parameter(
                'files', openapi.IN_FORM, description="List of files to upload", required=True,
                type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_FILE)
            )
        ],
        operation_description="Upload multiple files"
    )
    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist('files')

        if not files:
            return Response({"error": "No files provided."}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_files = []
        for file in files:
            file_path = os.path.join(INPUT_DIR, generate_compressed_filename(file.name))
            with open(file_path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)
            uploaded_files.append(file_path)

        try:
            output_files = compress_files_concurrently(uploaded_files)
            compressed_files = [
                os.path.join(settings.MEDIA_URL, 'output', os.path.basename(f))
                for f in output_files if os.path.exists(f)
            ]
            return Response({"files": compressed_files}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error during compression: {e}")
            return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)