from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

from views import IndexView, Error404View

from settings import DEBUG

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^b/', include('borme.urls')),

    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain'))
)

handler404 = Error404View

if DEBUG:
    from django.contrib import admin
    admin.autodiscover()

    urlpatterns += url(r'^admin/', include(admin.site.urls)),
    urlpatterns += url(r'^mongonaut/', include('mongonaut.urls')),
