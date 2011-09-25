"""
File Formtools Preview application.
Based on django.contrib.formtools.FormPreview
"""

try:
    import cPickle as pickle
except ImportError:
    import pickle

from django import forms
from django.conf import settings
from django.http import Http404
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.hashcompat import md5_constructor
from django.utils.crypto import constant_time_compare

from file_formpreview.forms.decorators import full_clean
from file_formpreview.forms.utils import security_hash
from file_formpreview.forms.fields import *
from file_formpreview.forms.widgets import *

SUFFIX = getattr(settings, 'SUFFIX', '_preview') # suffix to preview fields

AUTO_ID = 'formtools_%s' # Each form here uses this as its auto_id parameter.

__all__ = ('FileFormPreview',)

class FileFormPreview(object):
    preview_template = 'file_formpreview/preview.html'
    form_template = 'file_formpreview/form.html'

    def __init__(self, form_klass, preview_form_klass=None):
        "UPD: make self.form dynamic"
        self._form_klass = form_klass
        self._preview_form_klass = preview_form_klass
        self.state = {}

    @property
    def form(self):
        """
        Lazy evaluted Form class to inject some fields into form declaration
        ONLY on the first stage.

        It's a bit hacky, as the whole form.data is passed into
        `form.FIELD_NEEDED_CUSTOM_PREVIEW.custom_widget.value_from_datadict` 
        
        But as it's used TWICE:
            in BoundField.data (used to output preview stage) and
            in _clean for fields
        so, we CANNOT rewrite returned value
        from `widget.value_from_datadict`
        (it's used in validation further)

        Btw, http.QueryDict is immutable, too 
        """
        assert getattr(self, 'stage', None) is not None, \
            '%(cls)s.preview_form is used before %(cls)s calling' % \
            {'cls':self.__class__.__name__}

        #if not self._preview_form_klass:
        base = self._form_klass
        name = base.__class__.__name__ + 'Preview'
        namespace = dict(base.__dict__)
        
        # action stores uploaded file temponary
        widget = forms.HiddenInput

        for fname, field in namespace['base_fields'].iteritems():
            if isinstance(field, forms.FileField):
                namespace['base_fields'].update({fname+SUFFIX: PreviewPathField(
                    label='%s%s' % (fname, SUFFIX.lower()) , 
                    required=False,
                    widget=widget)})
            elif isinstance(field, forms.ImageField):
                namespace['base_fields'].update({fname+SUFFIX: PreviewImageField(
                    label='%s path' % fname, 
                    required=False,
                    widget=widget)})

        self._preview_form_klass = type(name, (base,), namespace)
        if self.stage == 'preview':
            self._preview_form_klass.full_clean = full_clean('preview')
        else:
            self._preview_form_klass.full_clean = full_clean('post')

        return self._preview_form_klass

    def __call__(self, request, *args, **kwargs):
        "UPD: store current stage"
        self.stage = {'1': 'preview', '2': 'post'}.get(request.POST.get(self.unused_name('stage')), 'preview')
        self.parse_params(*args, **kwargs)
        try:
            method = getattr(self, self.stage + '_' + request.method.lower())
        except AttributeError:
            raise Http404
        return method(request)

    def unused_name(self, name):
        """
        Given a first-choice name, adds an underscore to the name until it
        reaches a name that isn't claimed by any field in the form.

        This is calculated rather than being hard-coded so that no field names
        are off-limits for use in the form.

        UPD: Fixed form class pointer
        """
        while 1:
            try:
                f = self._form_klass.base_fields[name]
            except KeyError:
                break # This field name isn't being used by the form.
            name += '_'
        return name

    def preview_get(self, request):
        "Displays the form"
        f = self.form(auto_id=self.get_auto_id(), initial=self.get_initial(request))
        return render_to_response(self.form_template,
            self.get_context(request, f),
            context_instance=RequestContext(request))

    def preview_post(self, request):
        """
        Validates the POST data. If valid, displays the preview page. Else, redisplays form.
        
        UPD: takes FILES, gives original form
        """
        f = self.form(request.POST, request.FILES, auto_id=self.get_auto_id())
        context = self.get_context(request, f)
        if f.is_valid():
            self.process_preview(request, f, context)
            context['hash_field'] = self.unused_name('hash')
            context['hash_value'] = self.security_hash(request, f)
            context['original_form'] = self._form_klass(request.POST, request.FILES)
            return render_to_response(self.preview_template, context, context_instance=RequestContext(request))
        else:
            return render_to_response(self.form_template, context, context_instance=RequestContext(request))

    def _check_security_hash(self, token, request, form):
        expected = self.security_hash(request, form)
        if constant_time_compare(token, expected):
            return True
        else:
            # Fall back to Django 1.2 method, for compatibility with forms that
            # are in the middle of being used when the upgrade occurs. However,
            # we don't want to do this fallback if a subclass has provided their
            # own security_hash method - because they might have implemented a
            # more secure method, and this would punch a hole in that.

            # PendingDeprecationWarning <- left here to remind us that this
            # compatibility fallback should be removed in Django 1.5
            FormPreview_expected = FormPreview.security_hash(self, request, form)
            if expected == FormPreview_expected:
                # They didn't override security_hash, do the fallback:
                old_expected = security_hash(request, form)
                return constant_time_compare(token, old_expected)
            else:
                return False

    def post_post(self, request):
        """
        Validates the POST data. If valid, calls done(). Else, redisplays form.
        
        UPD: takes FILES
        """
        f = self.form(request.POST, request.FILES, auto_id=self.get_auto_id())
        if f.is_valid():
            if not self._check_security_hash(request.POST.get(self.unused_name('hash'), ''),
                                             request, f):
                return self.failed_hash(request) # Security hash failed.
            return self.done(request, f.cleaned_data)
        else:
            return render_to_response(self.form_template,
                self.get_context(request, f),
                context_instance=RequestContext(request))

    # METHODS SUBCLASSES MIGHT OVERRIDE IF APPROPRIATE ########################

    def get_auto_id(self):
        """
        Hook to override the ``auto_id`` kwarg for the form. Needed when
        rendering two form previews in the same template.
        """
        return AUTO_ID

    def get_initial(self, request):
        """
        Takes a request argument and returns a dictionary to pass to the form's
        ``initial`` kwarg when the form is being created from an HTTP get.
        """
        return {}

    def get_context(self, request, form):
        "Context for template rendering."
        return {'form': form, 'stage_field': self.unused_name('stage'), 'state': self.state}


    def parse_params(self, *args, **kwargs):
        """
        Given captured args and kwargs from the URLconf, saves something in
        self.state and/or raises Http404 if necessary.

        For example, this URLconf captures a user_id variable:

            (r'^contact/(?P<user_id>\d{1,6})/$', MyFormPreview(MyForm)),

        In this case, the kwargs variable in parse_params would be
        {'user_id': 32} for a request to '/contact/32/'. You can use that
        user_id to make sure it's a valid user and/or save it for later, for
        use in done().
        """
        pass

    def process_preview(self, request, form, context):
        """
        Given a validated form, performs any extra processing before displaying
        the preview page, and saves any extra data in context.
        """
        pass

    def security_hash(self, request, form):
        """
        Calculates the security hash for the given HttpRequest and Form instances.

        Subclasses may want to take into account request-specific information,
        such as the IP address.
        """
        return security_hash(request, form)

    def failed_hash(self, request):
        "Returns an HttpResponse in the case of an invalid security hash."
        return self.preview_post(request)

    # METHODS SUBCLASSES MUST OVERRIDE ########################################

    def done(self, request, cleaned_data):
        """
        Does something with the cleaned_data and returns an
        HttpResponseRedirect.
        """
        raise NotImplementedError('You must define a done() method on your %s subclass.' % self.__class__.__name__)