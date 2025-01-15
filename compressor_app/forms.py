from django import forms

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True  # Explicitly enable multiple file selection

class PDFUploadForm(forms.Form):
    files = forms.FileField(
        widget=MultipleFileInput(attrs={'multiple': True}),
        label="Upload PDF Files",
    )
