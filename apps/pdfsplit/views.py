import os
import PyPDF2
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.conf import settings

def upload_pdf(request):
    if request.method == 'POST' and request.FILES.get('file'):
        # Handle PDF upload and extract page count
        pdf_file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(pdf_file.name, pdf_file)
        uploaded_file_path = fs.path(filename)
        
        # Open the uploaded PDF to extract page count
        with open(uploaded_file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)  # Use PdfReader instead of PdfFileReader
            pages = [i for i in range(len(reader.pages))]
        
        return JsonResponse({
            'success': True,
            'filename': filename,
            'pages': pages
        })

    return render(request, 'public/pdfsplit.html')  # Render the template to upload PDF

def split_pdf(request):
    if request.method == 'POST':
        selected_pages = request.POST.getlist('selected_pages[]')
        pdf_file_path = request.POST.get('pdf_file_path')

        if not selected_pages:
            return JsonResponse({'success': False, 'message': 'No pages selected'})

        # Make sure the file path is correct
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        original_pdf_path = fs.path(pdf_file_path)

        if not os.path.exists(original_pdf_path):
            return JsonResponse({'success': False, 'message': 'PDF file not found'})

        try:
            with open(original_pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                writer = PyPDF2.PdfWriter()

                for page_num in selected_pages:
                    if int(page_num) < len(reader.pages):
                        writer.add_page(reader.pages[int(page_num)])

                # Save the output PDF
                output_pdf_path = os.path.join(settings.MEDIA_ROOT, f"split_{os.path.basename(pdf_file_path)}")
                with open(output_pdf_path, 'wb') as output_pdf:
                    writer.write(output_pdf)

                # Return the URL for the new PDF file
                output_pdf_url = settings.MEDIA_URL + f"split_{os.path.basename(pdf_file_path)}"

                return JsonResponse({
                    'success': True,
                    'pdf_url': output_pdf_url
                })

        except Exception as e:
            # Log the error for debugging purposes
            print(f"Error during PDF splitting: {e}")
            return JsonResponse({'success': False, 'message': f'Error during PDF splitting: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Invalid request'})
