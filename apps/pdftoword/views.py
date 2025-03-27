import os
import subprocess
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import render
from django.conf import settings

def pdf_to_word_page(request):
    """Renders the PDF to Word conversion page."""
    return render(request, "public/pdf_to_word.html")

@csrf_exempt
def pdf_to_word(request):
    if request.method == "POST" and request.FILES.get("pdf_file"):
        pdf_file = request.FILES["pdf_file"]

        # Save uploaded file
        pdf_path = default_storage.save(f"uploads_pdf_to_word/{pdf_file.name}", ContentFile(pdf_file.read()))
        pdf_full_path = default_storage.path(pdf_path)

        # Define output directory and file name
        output_dir = os.path.dirname(pdf_full_path)
        docx_filename = os.path.splitext(os.path.basename(pdf_full_path))[0] + ".docx"
        docx_path = os.path.join(output_dir, docx_filename)

        # Convert PDF to DOCX using LibreOffice with the correct filter
        try:
            result = subprocess.run(
                [
                    "libreoffice",
                    "--headless",
                    "--infilter=writer_pdf_import",
                    "--convert-to", "docx",
                    "--outdir", output_dir,
                    pdf_full_path
                ],
                capture_output=True,
                text=True,
                check=True
            )
            print("LibreOffice Output:", result.stdout)
            print("LibreOffice Error:", result.stderr)

            # Check if conversion was successful
            if os.path.exists(docx_path):
                download_url = f"{settings.MEDIA_URL}uploads_pdf_to_word/{docx_filename}"
                return JsonResponse({"success": True, "download_url": download_url})

        except subprocess.CalledProcessError as e:
            return JsonResponse({"error": f"Conversion failed: {e.stderr}"}, status=500)

        return JsonResponse({"error": "File conversion failed"}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)
