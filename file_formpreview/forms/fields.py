from django import forms

from file_formpreview.forms.widgets import *

__all__ = ('PreviewField', 'PreviewPathField',
        'PreviewFileField', 'PreviewImageField', 'PreviewCSVFileField')


class PreviewField(object):
    """
    Mixin to detect File- and Image- classes through `isinstance`

    Owerride them directly
    """
    pass

    def __init__(self, **kwargs):
        """ Detect some missing arguments passed to __init__ """

        if 'preview_widget' in kwargs:
            self.preview_widget = kwargs.pop('preview_widget')

        if isinstance(self, forms.ImageField):
            forms.ImageField.__init__(self, **kwargs)
        elif isinstance(self, forms.FileField):
            forms.FileField.__init__(self, **kwargs)
        else:
            super(self.__class__, self).__init__(**kwargs)
        

# these are for you: define your form fieldswith them

class PreviewFileField(PreviewField, forms.FileField):
    preview_widget = PreviewFileWidget

class PreviewCSVFileField(PreviewFileField):
    preview_widget = PreviewCSVFileWidget

    def to_python(self, data):
        """
        Checks if file is CSV-parseable
        """
        pass

class PreviewImageField(PreviewField, forms.ImageField):
    preview_widget = PreviewImageWidget


# this is for me :) 

class PreviewPathField(forms.CharField):
    widget = forms.HiddenInput


