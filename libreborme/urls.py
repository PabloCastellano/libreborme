from django.conf.urls import include, url
from django.conf.urls.static import static
from django.views.generic.base import TemplateView

from django.conf import settings

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name="libreborme/index.html"), name='home'),
    url(r'^borme/', include('borme.urls')),

    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    url(r'^humans\.txt$', TemplateView.as_view(template_name='humans.txt', content_type='text/plain')),

    url(r'^about/$', TemplateView.as_view(template_name="libreborme/about.html"), name='about'),
    url(r'^contact/$', TemplateView.as_view(template_name="libreborme/contact.html"), name='contact'),
    url(r'^cookies/$', TemplateView.as_view(template_name="libreborme/cookies.html"), name='cookies'),
    url(r'^developers/$', TemplateView.as_view(template_name="libreborme/developers.html"), name='developers'),
    url(r'^services/$', TemplateView.as_view(template_name="libreborme/services.html"), name='services'),
    url(r'^support/$', TemplateView.as_view(template_name="libreborme/support.html"), name='support'),
    url(r'^supporters/$', TemplateView.as_view(template_name="libreborme/supporters.html"), name='supporters'),
]


if settings.DEBUG:
    from django.contrib import admin
    admin.autodiscover()

    urlpatterns += url(r'^admin/', include(admin.site.urls)),
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
