import os
import tempfile

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django import forms
from django.conf import settings

from file_formpreview.forms.fields import *
from file_formpreview.forms.utils import mkdir_p

SUFFIX = getattr(settings, 'SUFFIX', '_preview') # suffix to preview fields

def full_clean(stage):
    """
    A decorator, that returns different ``full_clean`` methods
    depending on the stage

    Trick is:
    in preview stage after running `full_clean` on original form
    drop all previews and fill-in *_path fields because:
        - it's needed by `get_security_hash` as it wont hash files
        - after preview stage in POST it wont pass validation anyway

    in post stage it just:
        - removes preview fields BEFORE validation
        - pushes tmp-paths into 'cleaned_data'
    as user is interested in that vary value in `done` function,
    anyway, ModelForm uses it for saving instance, too
    """
    def wrapper(form):

        if stage == 'post':
            for fname, field in form.fields.items():
                if isinstance(field, PreviewPathField):
                    original_fname = fname.replace(SUFFIX, '')
                    form.fields.pop(original_fname)

        super(form.__class__, form).full_clean()

        if form.files: # i.e. if request.POST
            for fname, field in form.fields.items():
                # store file, add path
                if isinstance(field, PreviewField) and stage == 'preview':
                    # work around: first fetch file, then drop field, as
                    # it cannot be used in security hash calculation
                    fd = StringIO()
                    upload = form.files[fname]
                    for chunk in upload.chunks():
                        fd.write(chunk)
                    fd.seek(0)

                    form.fields.pop(fname)

                    # create dirs for tmp file
                    # FIXME: still passed request as None, as not needed
                    tmp_dir = os.path.join(
                        settings.MEDIA_ROOT,
                        'uploads',
                        datetime.now().strftime('%Y%m%d'),
                        security_hash(None, form)) 
                    mkdir_p(tmp_dir)

                    tmp_file = tempfile.NamedTemporaryFile(dir=tmp_dir, delete=False)
                    tmp_file.write(fd.read())
                    tmp_file.flush()

                    preview_fname = fname + SUFFIX
                    form.cleaned_data[preview_fname] = tmp_file.name
                    form.data[preview_fname] = tmp_file.name # actually used for initial

                elif isinstance(field, PreviewPathField) and stage == 'post':
                    original_fname = fname.replace(SUFFIX, '')
                    fd = StringIO()
                    with open(form.cleaned_data[original_fname]) as tmp_file:
                        fd.write(tmp_file.read())
                    fd.seek(0)
                    form.cleaned_data[original_fname] = fd

    return wrapper
