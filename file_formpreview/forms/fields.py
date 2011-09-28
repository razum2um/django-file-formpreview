from django import forms

from file_formpreview.forms.widgets import *

__all__ = ('PreviewField', 'PreviewPathField',
        'PreviewFileField', 'PreviewImageField')


class PreviewField(object):
    """
    Mixin to detect File- and Image- classes through `isinstance`

    Owerride them directly
    """
    pass
    #preview_widget = PreviewFileWidget
    #@property
    #def widget(self):
    #    raise NotImplementedError(
    #        "Define wigdet property in your %(cls)s declaration" % \
    #        self.__class__.__name__)

    def __init__(self, *args, **kwargs):
        """ Detect some missing arguments passed to __init__ """

        if 'preview_widget' in kwargs:
            self.preview_widget = kwargs.pop('preview_widget')

        # as THIS class is first in __bases__ -> we cannot call ``super``
        # FIXME: make it more explicit
        assert len(self.__class__.__bases__) == 2, ('Please, \
            use multiple inheritance for %(cls)s' % self.__class__.__name__)

        field_klass = self.__class__.__bases__[1]
        field_klass.__init__(self, *args, **kwargs)
        

# these are for you: define your form fieldswith them

class PreviewFileField(PreviewField, forms.FileField):
    preview_widget = PreviewFileWidget

class PreviewImageField(PreviewField, forms.ImageField):
    preview_widget = PreviewImageWidget


# this is for me :) 

class PreviewPathField(forms.CharField):
    widget = forms.HiddenInput


