from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from PyPDF2 import PdfMerger
from django.conf import settings
import os
from django.core.files.storage import default_storage

def merge_pdfs_view(request):
    if request.method == 'POST' and request.FILES.getlist('pdf_files'):
        pdf_files = request.FILES.getlist('pdf_files')
        merged_pdf_path = os.path.join(settings.MEDIA_ROOT, 'merged_output.pdf')
        
        # Create PdfMerger object to merge the PDFs
        merger = PdfMerger()
        
        # Append PDFs in the specified order
        for pdf_file in pdf_files:
            temp_file_path = os.path.join(settings.MEDIA_ROOT, pdf_file.name)
            with open(temp_file_path, 'wb') as f:
                for chunk in pdf_file.chunks():
                    f.write(chunk)
            merger.append(temp_file_path)
        
        # Write the merged PDF to a file
        merger.write(merged_pdf_path)
        merger.close()
        
        # Clean up temporary files
        for pdf_file in pdf_files:
            temp_file_path = os.path.join(settings.MEDIA_ROOT, pdf_file.name)
            os.remove(temp_file_path)
        
        # Open the merged PDF file for download
        with open(merged_pdf_path, 'rb') as merged_pdf:
            response = HttpResponse(merged_pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="merged_output.pdf"'
            return response
        
    return render(request, 'public/merge_pdfs.html')
