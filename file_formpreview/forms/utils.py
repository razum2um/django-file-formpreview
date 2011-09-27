import os, errno

try:
    import cPickle as pickle
except ImportError:
    import pickle

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.hashcompat import md5_constructor

# helper for shell `mkdir -p` equivalent
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise

def security_hash(form, *args):
    """
    Calculates a security hash for the given Form instance.

    This creates a list of the form field names/values in a deterministic
    order, pickles the result with the SECRET_KEY setting, then takes an md5
    hash of that.
    
    UPD: remove dependance from request, hash FileField.file.name instead of context
    """
    import warnings
    warnings.warn("security_hash is deprecated; use form_hmac instead",
                  PendingDeprecationWarning)
    data = []
    for bf in form:
        # Get the value from the form data. If the form allows empty or hasn't
        # changed then don't call clean() to avoid trigger validation errors.
        if form.empty_permitted and not form.has_changed():
            value = bf.data or ''
        else:
            value = bf.field.clean(bf.data) or ''
        if isinstance(value, basestring):
            value = value.strip()

        # work around as we cannot (needn't) pickle files
        if isinstance(value, InMemoryUploadedFile):
            data.append((bf.name, value.size))
        else:
            data.append((bf.name, value))
        
    data.extend(args)
    data.append(settings.SECRET_KEY)

    # Use HIGHEST_PROTOCOL because it's the most efficient. It requires
    # Python 2.3, but Django requires 2.4 anyway, so that's OK.
    pickled = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)

    return md5_constructor(pickled).hexdigest()

