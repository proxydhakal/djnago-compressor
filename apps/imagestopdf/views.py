import os
import uuid
from django.shortcuts import render
from django.http import JsonResponse
from PIL import Image
from django.conf import settings

ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp']

def upload_directory():
    directory = os.path.join(settings.MEDIA_ROOT, "uploads_images_to_pdf")
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def images_to_pdf(request):
    if request.method == "POST" and request.FILES.getlist("image_files"):
        images = []
        invalid_files = []

        for image_file in request.FILES.getlist("image_files"):
            # Check file type
            if image_file.content_type not in ALLOWED_IMAGE_TYPES:
                invalid_files.append(f"{image_file.name} - Invalid file type")
                continue

            try:
                # Check if file is empty
                if image_file.size == 0:
                    invalid_files.append(f"{image_file.name} - Empty file")
                    continue

                # Try to open and convert the image
                image = Image.open(image_file).convert("RGB")
                images.append(image)
            except Exception as e:
                invalid_files.append(f"{image_file.name} - Unable to process file")

        if images:
            pdf_name = f"{uuid.uuid4()}.pdf"
            pdf_path = os.path.join(upload_directory(), pdf_name)
            images[0].save(pdf_path, save_all=True, append_images=images[1:])
            response_data = {"pdf_url": os.path.join(settings.MEDIA_URL, "uploads_images_to_pdf", pdf_name)}

            if invalid_files:
                response_data["invalid_files"] = invalid_files

            return JsonResponse(response_data)

        return JsonResponse({"error": "No valid images uploaded."}, status=400)

    return render(request, "public/images_to_pdf.html")
