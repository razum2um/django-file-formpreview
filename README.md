Django File FormPreview
===========

The package provides functionality written in `bug#7808 <https://code.djangoproject.com/ticket/7808>`_

Technical notes
---------------

It provides two-step form submitting and actually based on ``django.contrib.formtools.FormPreview``, 
but there are many updates, so it isn't subclassed

First, it validates form, uploads file and stores its name.

Then, it injects needing *_path fields to point correspondong files

In the second POST step it uses path given in the hidden *_path fields.

Additionally, it can render some fields from original form, if they are subclassed from ``PreviewField`` as *_preview fields

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
        'file_formpreview',
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

* ``<YYmmdd>`` is somethind like "20110926"
* ``<hash>`` is unique value calculated for every form

Default templates will behave like this:

* for PreviewFileField => prints first 1024 bytes (raw), see PreviewFileWidget
* for PreviewImageField => displays the image (see Notes), see PreviewImageWidget

Configuration
-------------

Available in settings.py:

* UPLOAD_DIR - default: ``os.path.join(settings.MEDIA_ROOT, 'preview'))`` (**Note: it is autocleaned!**)
* OUTDATED_DAYS - default: 2, leave only todays+yesterdays, everything older in UPLOAD_DIR gets removed
* PREVIEW_SUFFIX - default: '_preview' , render them in preview stage
* PATH_SUFFIX - default: '_path' , are hidden, store paths to uploaded files

Available properties in your FileFormPreview subclass:

* preview_template, form_template - default: 'file_formpreview/preview.html', 'file_formpreview/form.html' respectively

Available preview render configuration:

* subclass needed Widget, pass it as parameter to ``PreviewField`` and rewrite ``render`` method

If you need something else, subclass FileFormPreview and implement ``process_preview``
to get extended context in the preview template

Notes
=====

**ATTENTION:** library doesn't check vulnerabilities like script uploads

**Make sure you've setup webserver not to execute files from MEDIA_ROOT
or give other upload_tmp parameter**
