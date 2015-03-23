from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from views import IndexView

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^b/', include('borme.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^mongonaut/', include('mongonaut.urls')),
)
