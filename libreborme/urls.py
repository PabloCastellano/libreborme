from django.urls import include, path
from django.views.generic.base import TemplateView

from . import views
from .settings import DEBUG

t = TemplateView.as_view

urlpatterns = [
    path('', t(template_name="libreborme/index.html"), name='home'),
    path('borme/', include('borme.urls')),
    path('', include('alertas.urls')),

    path('robots.txt', views.robotstxt),
    path('humans.txt', t(template_name='humans.txt', content_type='text/plain')),

    path('about/', views.AboutView.as_view(), name='about'),
    path('aviso-legal/', views.AvisoLegalView.as_view(), name='aviso_legal'),
    path('contact/', t(template_name="libreborme/contact.html"), name='contact'),
    path('cookies/', t(template_name="libreborme/cookies.html"), name='cookies'),
    path('developers/', t(template_name="libreborme/developers.html"), name='developers'),
    path('services/', t(template_name="libreborme/services.html"), name='services'),
    path('support/', t(template_name="libreborme/support.html"), name='support'),
    path('supporters/', t(template_name="libreborme/supporters.html"), name='supporters'),

    # Stripe
    path('payment-form', views.payment_form),
    path('checkout', views.checkout, name="checkout_page"),


    # Django site authentication urls (login, logout, password management...)
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register', views.register, name='register'),
]

if DEBUG:
    from django.contrib import admin
    admin.autodiscover()

    urlpatterns += path('admin/', admin.site.urls),

    import debug_toolbar
    urlpatterns += path('__debug__/', include(debug_toolbar.urls)),
