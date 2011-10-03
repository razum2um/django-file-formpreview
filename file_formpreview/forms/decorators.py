import os
import shutil
from datetime import datetime

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django import forms
from django.conf import settings

from file_formpreview.forms.fields import *
from file_formpreview.forms.utils import mkdir_p, security_hash

PREVIEW_SUFFIX = getattr(settings, 'PREVIEW_SUFFIX', '_preview')  # suffix to preview fields
PATH_SUFFIX = getattr(settings, 'PATH_SUFFIX', '_path')  # suffix to preview fields
UPLOAD_DIR = getattr(settings, 'UPLOAD_DIR', os.path.join(settings.MEDIA_ROOT, 'preview'))
OUTDATED_DAYS = getattr(settings, 'OUTDATED_DAYS', 2)  # mark yesterdays dirs for deletion

TODAYS_DIR = datetime.now().strftime('%Y%m%d')

if OUTDATED_DAYS < 2:
    OUTDATED_DAYS = 2  # dont allow to remove yesterdays temponaries

def upload_cleanup():
    """
    Autoclean all previous files because in current format
    int(yesterday_name) < int(today_name)
    """
    outdates_dirs = []
    for name in os.listdir(UPLOAD_DIR):
        try:
            int(name)
        except ValueError:
            outdates_dirs.append(name)
        else:
            if int(name) <= int(TODAYS_DIR) - OUTDATED_DAYS:
                outdates_dirs.append(name)
    for outdated in outdates_dirs:
        shutil.rmtree(os.path.join(UPLOAD_DIR, outdated))

def preview_full_clean(form):
    """
    In ``preview_post`` stage after running ``full_clean`` on original form
        - it drops all file fields and fill-in *_path fields

    because after in ``post_post`` stage it wont pass validation anyway,
    user doesn't upload file twice

    """

    super(form.__class__, form).full_clean()

    file_fields = [(fname, field) for fname, field in form.fields.iteritems()
        if isinstance(field, forms.FileField)]

    for fname, field in file_fields:
        tmp_dir = os.path.join(
            UPLOAD_DIR,
            TODAYS_DIR,
            security_hash(form)) 
        mkdir_p(tmp_dir)

        upload_cleanup()

        upload = form.cleaned_data[fname]

        if not upload:
            return  # just nop

        fd_name = os.sep.join((tmp_dir, upload.name))
        fd = open(fd_name, 'w')
        for chunk in upload.chunks():
            fd.write(chunk)
        fd.flush()

        # required for ImageField: django uses just .read() 
        # into PIL.Image() - otherwise it will be given empty file
        upload.seek(0)

        form.fields.pop(fname)

        path_fname = fname + PATH_SUFFIX
        form.cleaned_data[path_fname] = fd.name  # in view
        form.data[path_fname] = fd.name  # in template, as initial

        if isinstance(field, PreviewField):
            preview_fname = fname + PREVIEW_SUFFIX
            form.cleaned_data[preview_fname] = fd.name  # in view
            form.data[preview_fname] = fd.name  # in template, as initial

def post_full_clean(form):
    """
    In ``post_post`` stage it just:
        - removes file fields BEFORE validation (no upload was done)
        - pushes tmp-paths into 'cleaned_data'

    As user is interested in that vary value in `done` function,
    anyway, ModelForm uses it for saving instance, too
    """
    for fname, field in form.fields.items():
        if isinstance(field, PreviewPathField):
            original_fname = fname.replace(PATH_SUFFIX, '')
            form.fields.pop(original_fname)

    super(form.__class__, form).full_clean()

    for fname, field in form.fields.items():
        if isinstance(field, PreviewPathField):
            original_fname = fname.replace(PATH_SUFFIX, '')
            fd = StringIO()
            with open(form.cleaned_data[fname]) as tmp_file:
                fd.write(tmp_file.read())
            fd.seek(0)
            form.cleaned_data[original_fname] = fd
