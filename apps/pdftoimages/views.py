import os
import uuid
import zipfile
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse, HttpResponse
from pdf2image import convert_from_path
from django.conf import settings
from io import BytesIO

def upload_directory():
    directory = os.path.join(settings.MEDIA_ROOT, "uploads_pdf_to_images")
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def pdf_to_images(request):
    if request.method == "POST" and request.FILES.get("pdf_file"):
        pdf_file = request.FILES["pdf_file"]
        file_name = f"{uuid.uuid4()}.pdf"
        upload_path = os.path.join(upload_directory(), file_name)

        # Save the PDF to the appropriate location
        with open(upload_path, 'wb') as f:
            for chunk in pdf_file.chunks():
                f.write(chunk)

        try:
            # Convert the PDF to images
            images = convert_from_path(upload_path)

            image_urls = []
            image_paths = []
            for i, image in enumerate(images):
                image_name = f"{uuid.uuid4()}.png"
                image_path = os.path.join(upload_directory(), image_name)
                image.save(image_path, "PNG")
                image_urls.append(os.path.join(settings.MEDIA_URL, "uploads_pdf_to_images", image_name))
                image_paths.append(image_path)

            # Check if there are multiple images, if so create a zip file
            if len(image_urls) > 1:
                zip_name = f"{uuid.uuid4()}.zip"
                zip_path = os.path.join(upload_directory(), zip_name)
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for image_path in image_paths:
                        zipf.write(image_path, os.path.basename(image_path))

                zip_url = os.path.join(settings.MEDIA_URL, "uploads_pdf_to_images", zip_name)
                # Remove the individual images as they are now in the zip
                for image_path in image_paths:
                    os.remove(image_path)

                return JsonResponse({"zip": zip_url})

            # If only one image, return the image URL
            return JsonResponse({"images": image_urls})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return render(request, "public/pdf_to_images.html")
