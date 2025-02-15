import os
import zipfile
import subprocess
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def convert_docx_to_pdf(docx_path):
    """ Convert DOCX to PDF while preserving layout, images, fonts, etc. """
    output_dir = os.path.dirname(docx_path)
    command = [
        "libreoffice",
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        output_dir,
        docx_path
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return docx_path.replace(".docx", ".pdf")

def upload_and_convert(request):
    if request.method == "POST" and request.FILES.getlist('files[]'):
        uploaded_files = request.FILES.getlist('files[]')
        pdf_files = []

        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            if not file_name.endswith('.docx'):
                continue  # Skip non-DOCX files

            # Save the uploaded file
            file_path = default_storage.save(f"temp/{file_name}", ContentFile(uploaded_file.read()))
            full_file_path = default_storage.path(file_path)
            
            # Convert DOCX to PDF
            pdf_path = convert_docx_to_pdf(full_file_path)
            pdf_files.append(pdf_path)

        if len(pdf_files) == 1:
            # Return a single PDF file for download
            with open(pdf_files[0], 'rb') as pdf:
                response = HttpResponse(pdf.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_files[0])}"'
            return response
        else:
            # Create a ZIP archive for multiple PDFs
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for pdf_file in pdf_files:
                    zip_file.write(pdf_file, os.path.basename(pdf_file))

            zip_buffer.seek(0)
            response = HttpResponse(zip_buffer, content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="converted_pdfs.zip"'
            return response

    return render(request, 'public/docxtopdf.html')
