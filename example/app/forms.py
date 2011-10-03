from django import forms

from file_formpreview.forms.fields import PreviewFileField, PreviewImageField, PreviewCSVFileField
from file_formpreview.forms.forms import FileFormPreview

class MyForm(forms.Form):
    raw_file = PreviewFileField(required=False)
    image_file = PreviewImageField(required=False)
    csv_file = PreviewCSVFileField()

class MyFileFormPreview(FileFormPreview):
    pass

