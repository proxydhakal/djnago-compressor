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
    Generate a new filename with the format Shekhar-Compress_timestamp.extension
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')  # Include microseconds for uniqueness
    name, extension = os.path.splitext(original_filename)
    return original_filename #f"{name}-Compress_{timestamp}{extension}"

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
            resources = page.get('/Resources', {})
            if '/XObject' in resources:
                xobjects = resources['/XObject']
                for obj in xobjects:
                    if xobjects[obj]['/Subtype'] == '/Image':
                        has_images = True
                        break

            # If we found both text and images, we can stop checking
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
        logger.info(f"Compressed {input_pdf} to {output_pdf} using {compression_level} settings.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error compressing {input_pdf}: {e}")

def compress_image(input_image, output_image):
    """
    Compress an image (JPEG/PNG) without changing DPI or pixel dimensions.
    """
    try:
        with Image.open(input_image) as img:
            # Save the image with reduced quality, without changing DPI or pixel dimensions
            img.save(output_image, quality=50, optimize=True)
            logger.info(f"Compressed image {input_image} to {output_image}")
    except Exception as e:
        logger.error(f"Error compressing image {input_image}: {e}")
        
def compress_files_sequentially(files):
    """
    Compress multiple files sequentially.
    """
    output_files = []

    for file in files:
        input_path = os.path.join(INPUT_DIR, file.name)  # ✅ File object used correctly
        output_filename = generate_compressed_filename(file.name)
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        # Save uploaded file
        try:
            with open(input_path, 'wb') as f:
                for chunk in file.chunks():  # ✅ 'file' is now an InMemoryUploadedFile
                    f.write(chunk)
            logger.info(f"File saved: {input_path}")
        except IOError as e:
            logger.error(f"Failed to save {file.name}: {e}")
            continue

        # Determine file extension and choose the appropriate compression method
        file_extension = file.name.split('.')[-1].lower()
        if file_extension in ['pdf']:
            compress_pdf(input_path, output_path)
        elif file_extension in ['jpg', 'jpeg', 'png']:
            compress_image(input_path, output_path)
        else:
            logger.warning(f"Unsupported file type: {file_extension}")
            continue

        # Log compression details
        try:
            original_size = os.path.getsize(input_path)
            compressed_size = os.path.getsize(output_path)
            file_type = file_extension

            # Create a FileCompressLog entry
            FileCompressLog.objects.create(
                file_name=file.name,
                original_size=original_size,
                compressed_size=compressed_size,
                file_type=file_type
            )

            logger.info(f"Compression logged for {file.name}: {original_size} -> {compressed_size} bytes")
        except Exception as e:
            logger.error(f"Error logging compression for {file.name}: {e}")

        output_files.append(output_path)

    return output_files



def upload_and_compress(request):
    """
    Handle file upload and compression.
    """
    if request.method == "POST":
        files = request.FILES.getlist('pdfFiles[]')

        if not files:
            return JsonResponse({"error": "No files provided."}, status=400)

        output_files = compress_files_sequentially(files)

        compressed_files = [
            os.path.join(settings.MEDIA_URL, 'output', os.path.basename(f))
            for f in output_files if os.path.exists(f)
        ]
        return JsonResponse({"files": compressed_files}, status=200)

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
        operation_description="Upload multiple files. Supported Files PDF, PNG, JPG, JPEG"
    )
    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist('files')
        if not files:
            return Response({"error": "No files provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Pass file objects directly instead of saving them first
        try:
            output_files = compress_files_sequentially(files)  # ✅ Pass files instead of file paths
            compressed_files = [
                os.path.join(settings.MEDIA_URL, 'output', os.path.basename(f))
                for f in output_files if os.path.exists(f)
            ]
            return Response({"files": compressed_files}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error during compression: {e}")
            return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
