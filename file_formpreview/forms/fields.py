from django import forms

from file_formpreview.forms.widgets import *

__all__ = ('PreviewField', 'PreviewPathField',
        'PreviewFileField', 'PreviewImageField')


class PreviewField(object):
    """
    Mixin to detect File- and Image- classes through `isinstance`

    Owerride them directly
    """
    preview_widget = PreviewFileWidget

    def _pre_init(self, *args, **kwargs):
        """ Detect some missing arguments passed to __init__ """

        if 'preview_widget' in kwargs:
            self.preview_widget = kwargs.pop('preview_widget')

class PreviewPathField(forms.CharField):
    pass

class PreviewFileField(forms.FileField, PreviewField):
    preview_widget = PreviewFileWidget
    def __init__(self, *args, **kwargs):
        self._pre_init(self, *args, **kwargs)
        super(PreviewFileField, self).__init__(*args, **kwargs)

class PreviewImageField(forms.ImageField, PreviewField):
    preview_widget = PreviewImageWidget
    def __init__(self, *args, **kwargs):
        self._pre_init(self, *args, **kwargs)
        super(PreviewImageField, self).__init__(*args, **kwargs)
