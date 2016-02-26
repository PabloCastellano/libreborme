from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

from .views import IndexView, CookiesView
from .settings import DEBUG

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^borme/', include('borme.urls')),

    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    url(r'^humans\.txt$', TemplateView.as_view(template_name='humans.txt', content_type='text/plain')),
    url(r'^politica-de-cookies$', CookiesView.as_view(), name='cookies')
)

if DEBUG:
    from django.contrib import admin
    admin.autodiscover()

    urlpatterns += url(r'^admin/', include(admin.site.urls)),
