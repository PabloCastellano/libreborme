from django.urls import include, path
from django.views.generic.base import TemplateView

from . import views
from .settings import DEBUG

urlpatterns = [
    path('', TemplateView.as_view(template_name="libreborme/index.html"), name='home'),
    path('borme/', include('borme.urls')),

    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('humans.txt', TemplateView.as_view(template_name='humans.txt', content_type='text/plain')),

    path('about/', views.AboutView.as_view(), name='about'),
    path('aviso-legal/', views.AvisoLegalView.as_view(), name='aviso_legal'),
    path('contact/', TemplateView.as_view(template_name="libreborme/contact.html"), name='contact'),
    path('cookies/', TemplateView.as_view(template_name="libreborme/cookies.html"), name='cookies'),
    path('developers/', TemplateView.as_view(template_name="libreborme/developers.html"), name='developers'),
    path('services/', TemplateView.as_view(template_name="libreborme/services.html"), name='services'),
    path('support/', TemplateView.as_view(template_name="libreborme/support.html"), name='support'),
    path('supporters/', TemplateView.as_view(template_name="libreborme/supporters.html"), name='supporters'),
]

if DEBUG:
    from django.contrib import admin
    admin.autodiscover()

    urlpatterns += path('admin/', admin.site.urls),
