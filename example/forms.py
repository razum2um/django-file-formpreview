from django import forms
from file_formpreview import FileFormPreview

class MyForm(forms.Form):
    raw_file = forms.FileField(u'Raw file')

class MyFileFormPreview(FileFormPreview):
    pass
