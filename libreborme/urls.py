from django.urls import include, path
from django.views.generic.base import TemplateView
from django.views.generic import RedirectView

from django_registration.backends.activation.views import RegistrationView

from . import views
from .forms import LBUserCreationForm
from .settings import DEBUG

t = TemplateView.as_view

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='borme-home')),
    path('index_old', t(template_name="libreborme/index.html"), name='home'),
    path('borme/', include('borme.urls')),
    path('dataremoval/', include('dataremoval.urls')),
    path('', include('alertas.urls')),

    path('robots.txt', views.robotstxt),
    path('humans.txt', t(template_name='humans.txt', content_type='text/plain')),

    path('about/', views.AboutView.as_view(), name='about'),
    path('aviso-legal/', views.AvisoLegalView.as_view(), name='aviso_legal'),
    path('contact/', t(template_name="libreborme/contact.html"), name='contact'),
    path('cookies/', t(template_name="libreborme/cookies.html"), name='cookies'),
    path('developers/', t(template_name="libreborme/developers.html"), name='developers'),
    path('services/', views.ServicesView.as_view(), name='services'),
    path('support/', t(template_name="libreborme/support.html"), name='support'),
    path('supporters/', t(template_name="libreborme/supporters.html"), name='supporters'),

    # dj-stripe
    path("stripe/", include("djstripe.urls", namespace="djstripe")),

    # django-registration
    path('accounts/register/', RegistrationView.as_view(form_class=LBUserCreationForm), name='django_registration_register'),
    path('accounts/', include('django_registration.backends.activation.urls')),

    # Django site authentication urls (login, logout, password management...)
    path('accounts/', include('django.contrib.auth.urls')),
]

if DEBUG:
    from django.contrib import admin
    admin.autodiscover()

    urlpatterns += path('admin/', admin.site.urls),

    # django-debug-toolbar
    import debug_toolbar
    urlpatterns += path('__debug__/', include(debug_toolbar.urls)),
