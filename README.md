Django File FormPreview
===========

The package provides functionality written in `bug#7808 <https://code.djangoproject.com/ticket/7808>`_

Technical notes
---------------

It provides two-step form submitting and actually inherit from ``django.contrib.formtools.FormPreview``.
First, it validates form, uploads file and stores its name.
Then, it injects needing *_path fields to point correspondong files
In the second POST step it uses path given in the hidden *_path fields.

Trying to submit another fiel path will fail, because file path depends on hash,
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

    class MyForm(forms.Form):
        ...
        ...
        def done(self, request, cleaned_data):
        """
        Does something with the cleaned_data and returns an
        HttpResponseRedirect.
        """
        ...

    # urls.py:

    from my_forms import MyForm
    from file_preview import FileFormPreview

    url('^add-upload/$', FileFormPreview(
            MyForm, 
            [upload_tmp='...',]
            [preview_template='...',]
            [form_template='...'])

    OR views.py:
    
    from my_forms import MyForm
    from file_preview import FileFormPreview

    def add_upload(request):
        ...
        return FilePreviewForm(MyForm)(request)

Default upload_tmp = ``settings.MEDIA_ROOT``, 
it creates under it following structure: ``YYYmmdd/<hash>/file_name.ext``
``YYmmdd`` is somethind like "20110926"
``<hash>`` is unique value calculated for every form

Default templates will behave like this:

* for FileField => prints first 1024 bytes (raw)

* for ImageField => displays the image (see Notes)

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
