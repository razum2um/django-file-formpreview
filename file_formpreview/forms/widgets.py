from django import forms

__all__ = ('PreviewWidget', 'PreviewFileWidget', 'PreviewImageWidget')


class PreviewWidget(forms.Widget):
    is_hidden = True
    def value_from_datadict(self, data, files, name):
        raise
        return data

class PreviewFileWidget(PreviewWidget):
    pass

class PreviewImageWidget(PreviewWidget):
    pass
