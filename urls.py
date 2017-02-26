from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^alertas/$', views.DashboardIndexView.as_view(), name='dashboard-index'),
    url(r'^alertas/list/$', views.AlertaListView.as_view(), name='alertas-list'),
    url(r'^alertas/billing/$', views.BillingView.as_view(), name='alertas-billing'),
    url(r'^alertas/billing/(?P<id>\d+)/$', views.BillingDetailView.as_view(), name='alertas-invoice-view'),
    url(r'^alertas/new/$', views.alerta_create, name='alertas-index'),
    url(r'^alertas/new/acto/$', views.alerta_acto_create, name='alertas-new-acto'),
    url(r'^alertas/new/person/$', views.alerta_person_create, name='alertas-new-person'),
    url(r'^alertas/new/company/$', views.alerta_company_create, name='alertas-new-company'),
    url(r'^alertas/(?P<id>\d+)/$', views.AlertaDetailView.as_view(), name='alertas-detail'),
    url(r'^alertas/remove/(?P<id>\d+)/$', views.alerta_remove, name='alerta-remove-acto'),
    url(r'^alertas/soporte/$', views.DashboardSupportView.as_view(), name='alertas-soporte'),
    url(r'^alertas/settings/$', views.DashboardSettingsView.as_view(), name='alertas-settings'),
    url(r'^alertas/settings/update/personal/$', views.settings_update_personal, name='alertas-settings-personal'),
    url(r'^alertas/settings/update/notifications/$', views.settings_update_notifications, name='alertas-settings-notifications'),
    url(r'^alertas/history/$', views.DashboardHistoryView.as_view(), name='dashboard-history'),
    
#    url(r'^(?P<id>\d+)/$', views.alertas_view, name='alertas-detail'),

    # Add Django site authentication urls (for login, logout, password management)
    url('^accounts/', include('django.contrib.auth.urls')),
]
