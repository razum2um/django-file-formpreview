Django File FormPreview
===========

The package provides functionality written in `bug#7808 <https://code.djangoproject.com/ticket/7808>`_

Technical notes
---------------

It provides two-step form submitting and actually inherit from ``django.contrib.formtools.FormPreview``.

First, it validates form, uploads file and stores its name.

Then, it injects needing *_path fields to point correspondong files

In the second POST step it uses path given in the hidden *_path fields.

Additionally, it can render some fields from original form, if they are subclassed from ``PreviewField``

Security
--------

Trying to submit another file path will fail, because file path depends on hash,
which is calculated from:

* other form field values
* file size
* origin file name
* django secret key

Usage
-----

    # settings.py:

    INSTALLED_APPS = (
        ...
        'file_preview',
        ...
    )

    # forms.py:

    from file_formpreview import FileFormPreview

    class MyFileFormPreview(FileFormPreview):
        ...
        [form_template = '...']
        [preview_template = '...']
        ...
        def done(self, request, cleaned_data):
            """
            Does something with the cleaned_data and returns an
            HttpResponseRedirect.
            """
            ...

    # urls.py:

        from my_forms import MyForm, MyFileFormPreview

        url('^add-upload/$', FileFormPreview(MyForm)

    OR views.py:
    
    from my_forms import MyForm, MyFileFormPreview

    def add_upload(request):
        ...
        return MyFilePreviewForm(MyForm)(request)

it creates under it following structure: ``<settings.UPLOAD_DIR>/<YYYmmdd>/<hash>/<uploaded_file_name.ext>``
``<YYmmdd>`` is somethind like "20110926"
``<hash>`` is unique value calculated for every form

Default templates will behave like this:

* for PreviewFileField => prints first 1024 bytes (raw), see PreviewFileWidget
* for PreviewImageField => displays the image (see Notes), see PreviewImageWidget

Configuration
-------------

Available in settings.py:

* UPLOAD_DIR - default: ``os.path.join(settings.MEDIA_ROOT, 'preview'))`` (**Note: it is autocleaned!**)
* OUTDATED_DAYS - default: 2, leave only todays+yesterdays, everything older in UPLOAD_DIR gets removed
* SUFFIX - default: '_preview', show these fields.data in ``preview_template``

Available properties in your FileFormPreview subclass:

* preview_template, form_template - default: 'file_formpreview/preview.html', 'file_formpreview/form.html' respectively

Available preview render configuration:

* subclass needed Widget, pass it as parameter to ``PreviewField`` and rewrite ``render`` method

Custom Preview Handling
-----------------------

Just define some methods with ``_preview`` suffix in your Form::

    class MyForm(forms.Form):
        my_file = forms.FileField(...)
        my_image = forms.ImageField(...)

        def my_file_preview(self, local_path):
            return open(local_path).read(1024)

        def my_image_preview(self, local_path):
            return mark_safe('<img src="/media/%s" />' % local_path) 

If you need something else, subclass FileFormPreview and implement ``process_preview``
to get extended context in the preview template

Notes
=====

**ATTENTION:** library doesn't check vulnerabilities like script uploads

**Make sure you've setup webserver not to execute files from MEDIA_ROOT
or give other upload_tmp parameter**
