import os
import shutil
import tempfile
from datetime import datetime

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django import forms
from django.conf import settings

from file_formpreview.forms.fields import *
from file_formpreview.forms.utils import mkdir_p, security_hash

SUFFIX = getattr(settings, 'SUFFIX', '_preview') # suffix to preview fields
OUTDATED_DAYS = getattr(settings, 'OUTDATED_DAYS', 1)  # mark yesterdays dirs for deletion

if OUTDATED_DAYS < 1:
    OUTDATED_DAYS = 1  # dont allow to remove todays temponaries

def full_clean(stage, method):
    """
    A decorator, that returns different ``full_clean`` methods
    depending on the stage

    Trick is:
    in ``preview_post`` stage after running ``full_clean`` on original form
        - it drops all file fields and fill-in *_path fields

    because after in ``post_post`` stage it wont pass validation anyway,
    user doesn't upload file twice

    in ``post_post`` stage it just:
        - removes file fields BEFORE validation (no upload was done)
        - pushes tmp-paths into 'cleaned_data'

    as user is interested in that vary value in `done` function,
    anyway, ModelForm uses it for saving instance, too
    """
    def wrapper(form):

        if stage == 'post' and method == 'post':
            for fname, field in form.fields.items():
                if isinstance(field, PreviewPathField):
                    original_fname = fname.replace(SUFFIX, '')
                    form.fields.pop(original_fname)

        super(form.__class__, form).full_clean()

        if stage == 'preview' and method == 'post':
            for fname, field in form.fields.items():
                if isinstance(field, forms.FileField) or \
                        isinstance(field, forms.ImageField):

                    upload_dir = os.path.join(
                        settings.MEDIA_ROOT,
                        'uploads')

                    todays_dir = datetime.now().strftime('%Y%m%d')
                    tmp_dir = os.path.join(
                        upload_dir,
                        todays_dir,
                        security_hash(form)) 
                    mkdir_p(tmp_dir)

                    # autoclean all previous files because in this format
                    # int(yesterday_name) < int(today_name)
                    outdates_dirs = []
                    for name in os.listdir(upload_dir):
                        try:
                            int(name)
                        except ValueError:
                            pass
                        else:
                            if int(name) <= int(todays_dir) - OUTDATED_DAYS:
                                outdates_dirs.append(name)
                    for outdated in outdates_dirs:
                        shutil.rmtree(os.path.join(upload_dir, outdated))

                    fd = tempfile.NamedTemporaryFile(dir=tmp_dir, delete=False)
                    fd_name = os.sep.join((tmp_dir, form.files[fname].name))
                    fd = open(fd_name, 'w')
                    upload = form.files[fname]
                    for chunk in upload.chunks():
                        fd.write(chunk)
                    fd.flush()

                    form.fields.pop(fname)

                    preview_fname = fname + SUFFIX
                    # for view
                    form.cleaned_data[preview_fname] = fd.name

                    # for template, actually - initial
                    form.data[preview_fname] = fd.name

        elif stage == 'post' and method == 'post':
            for fname, field in form.fields.items():
                if isinstance(field, PreviewPathField):
                    original_fname = fname.replace(SUFFIX, '')
                    fd = StringIO()
                    with open(form.cleaned_data[fname]) as tmp_file:
                        fd.write(tmp_file.read())
                    fd.seek(0)
                    form.cleaned_data[original_fname] = fd

    return wrapper
