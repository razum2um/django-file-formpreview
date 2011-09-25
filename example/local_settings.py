from django.conf import settings

INSTALLED_APPS = settings.INSTALLED_APPS + [
    'debug_toolbar',
    'django_extensions',
]
MIDDLEWARE_CLASSES = settings.MIDDLEWARE_CLASSES + (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}
