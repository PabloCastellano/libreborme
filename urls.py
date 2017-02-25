from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^alertas/$', views.AlertaListView.as_view(), name='alertas-index'),
    url(r'^alertas/new/$', views.AlertaCompanyCreateView.as_view(), name='alertas-index'),
    url(r'^alertas/(?P<id>\d+)/$', views.AlertaDetailView.as_view(), name='alertas-detail'),
#    url(r'^$', views.alertas_index, name='alertas-index'),
#    url(r'^(?P<id>\d+)/$', views.alertas_view, name='alertas-detail'),

    # Add Django site authentication urls (for login, logout, password management)
    url('^accounts/', include('django.contrib.auth.urls')),
]
