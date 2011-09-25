from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('views',
    (r'^upload/$', 'upload'),
)
