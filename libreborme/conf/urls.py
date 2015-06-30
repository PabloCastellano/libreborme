from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin

from django.views.generic.base import TemplateView

from .views import IndexView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^borme/', include('borme.urls')),

    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain'))
)

if settings.DEBUG:
    from django.contrib import admin
    admin.autodiscover()

    urlpatterns += url(r'^admin/', include(admin.site.urls)),
    urlpatterns += url(r'^mongonaut/', include('mongonaut.urls')),


if settings.DEBUG and settings.SERVE_STATIC:
    urlpatterns += patterns('django.contrib.staticfiles.views',
        url(r'^static/(?P<path>.*)$', 'serve'),
        url(r'^media/(?P<path>.*)$', 'serve'),
    )
