import os
import threading
import logging
import subprocess
from PIL import Image
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from datetime import datetime
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define input and output directories
INPUT_DIR = os.path.join(settings.MEDIA_ROOT, 'input')
OUTPUT_DIR = os.path.join(settings.MEDIA_ROOT, 'output')


def generate_compressed_filename(original_filename):
    """
    Generate a new filename with the format Shekhar-Compress_timestamp.extension
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    name, extension = os.path.splitext(original_filename)
    return f"Shekhar-Compress_{timestamp}{extension}"


def compress_pdf(input_pdf, output_pdf, compression_level="screen"):
    """
    Compress a single PDF using Ghostscript.
    """
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
            # Save the image with reduced quality, without changing DPI or pixel dimensions
            img.save(output_image, quality=50, optimize=True)
            logger.info(f"Compressed image {input_image} to {output_image}")
    except Exception as e:
        logger.error(f"Error compressing image {input_image}: {e}")


def compress_files_concurrently(files):
    """
    Compress multiple files concurrently using threads.
    """
    threads = []
    output_files = []

    for file in files:
        input_path = os.path.join(INPUT_DIR, file.name)
        output_filename = generate_compressed_filename(file.name)
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        # Save uploaded file
        try:
            with open(input_path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)
            logger.info(f"File saved: {input_path}")
        except IOError as e:
            logger.error(f"Failed to save {file.name}: {e}")
            continue

        # Determine file extension and choose the appropriate compression method
        file_extension = file.name.split('.')[-1].lower()
        if file_extension in ['pdf']:
            # Compress PDF files
            thread = threading.Thread(target=compress_pdf, args=(input_path, output_path))
        elif file_extension in ['jpg', 'jpeg', 'png']:
            # Compress image files
            thread = threading.Thread(target=compress_image, args=(input_path, output_path))
        else:
            logger.warning(f"Unsupported file type: {file_extension}")
            continue

        threads.append(thread)
        output_files.append(output_path)

    # Start and join threads
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    return output_files


def upload_and_compress(request):
    """
    Handle file upload and compression.
    """
    if request.method == "POST":
        files = request.FILES.getlist('files')

        # Ensure input and output directories exist
        os.makedirs(INPUT_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # Compress files (PDFs and images)
        try:
            output_files = compress_files_concurrently(files)

            # Prepare file URLs for download
            compressed_files = [
                os.path.join(settings.MEDIA_URL, 'output', os.path.basename(f))
                for f in output_files
            ]
            return JsonResponse({"files": compressed_files})
        except Exception as e:
            logger.error(f"Error during compression: {e}")
            return JsonResponse({"error": "Internal server error."}, status=500)

    return render(request, 'upload.html')
