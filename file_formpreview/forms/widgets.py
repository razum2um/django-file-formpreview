from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe

__all__ = ('PreviewWidget', 'PreviewFileWidget', 'PreviewImageWidget')


PREVIEW_SUFFIX = getattr(settings, 'PREVIEW_SUFFIX', '_preview')  # suffix to preview fields

class PreviewWidget(forms.Widget):
    pass

class PreviewFileWidget(PreviewWidget):
    def value_from_datadict(self, data, files, name):
        return files.get(name.replace(PREVIEW_SUFFIX, ''), None)

    def render(self, name, fd, attrs=None):
        if not fd:
            return mark_safe('')
        fd.seek(0)
        rendered = fd.read(1024)
        return mark_safe(rendered)

class PreviewImageWidget(PreviewWidget):
    def render(self, name, fd_path, attrs=None):
        if not fd_path:
            return mark_safe('')
        rel_path = fd_path.replace(settings.MEDIA_ROOT + '/', settings.MEDIA_URL)
        return mark_safe('<img src="%s" />' % rel_path)
