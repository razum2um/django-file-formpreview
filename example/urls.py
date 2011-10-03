from django.conf import settings
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('app.views',
    (r'^upload/$', 'upload'),
)

urlpatterns += patterns('',
    url(r'^media/(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True})
)
