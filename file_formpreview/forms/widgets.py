from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe

__all__ = ('PreviewWidget', 'PreviewFileWidget', 'PreviewImageWidget')


PREVIEW_SUFFIX = getattr(settings, 'PREVIEW_SUFFIX', '_preview')  # suffix to preview fields

class PreviewWidget(forms.Widget):
    #is_hidden = True
    def value_from_datadict(self, data, files, name):
        return files.get(name.replace(PREVIEW_SUFFIX, ''), None)
        #raise
        #return data

class PreviewFileWidget(PreviewWidget):
    def render(self, name, fd, attrs=None):
        if not fd:
            return mark_safe('')
        fd.seek(0)
        rendered = fd.read(1024)
        #raise
        #fd.close()
        return mark_safe(rendered)

class PreviewImageWidget(PreviewWidget):
    pass
