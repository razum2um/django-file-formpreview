from django import forms

from file_formpreview.forms.fields import PreviewFileField, PreviewImageField
from file_formpreview.forms.forms import FileFormPreview

class MyForm(forms.Form):
    raw_file = PreviewFileField(u'Raw file')
    #image_file = PreviewImageField(u'Image')

class MyFileFormPreview(FileFormPreview):
    pass
