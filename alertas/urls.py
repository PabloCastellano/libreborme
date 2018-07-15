from django.urls import include, path

from . import views

urlpatterns = [
    path('alertas/', views.MyAccountView.as_view(), name='dashboard-index'),
    path('alertas/events/', views.AlertaEventsView.as_view(), name='alertas-events'),
    path('alertas/list/', views.AlertaListView.as_view(), name='alertas-list'),
    path('alertas/subscriptions/', views.SubscriptionListView.as_view(), name='subscriptions-list'),
    path('alertas/billing/', views.BillingView.as_view(), name='alertas-billing'),
    path('alertas/billing/<id>/', views.BillingDetailView.as_view(), name='alertas-invoice-view'),
    path('alertas/payment/', views.PaymentView.as_view(), name='alertas-payment'),
    path('alertas/new/acto/', views.alerta_acto_create, name='alertas-new-acto'),
    path('alertas/new/person/', views.alerta_person_create, name='alertas-new-person'),
    path('alertas/new/company/', views.alerta_company_create, name='alertas-new-company'),
    path('alertas/<id>/', views.AlertaDetailView.as_view(), name='alertas-detail'),
    path('alertas/remove/acto/<id>/', views.alerta_remove_acto, name='alerta-remove-acto'),
    path('alertas/remove/person/<id>/', views.alerta_remove_person, name='alerta-remove-person'),
    path('alertas/remove/company/<id>/', views.alerta_remove_company, name='alerta-remove-company'),
    path('alertas/ayuda/', views.DashboardSupportView.as_view(), name='alertas-ayuda'),
    path('alertas/settings/', views.DashboardSettingsView.as_view(), name='alertas-settings'),
    path('alertas/settings/update/personal/', views.settings_update_personal, name='alertas-settings-personal'),
    path('alertas/settings/update/billing/', views.settings_update_billing, name='alertas-settings-billing'),
    path('alertas/settings/update/notifications/', views.settings_update_notifications, name='alertas-settings-notifications'),
    path('alertas/settings/update/stripe/', views.settings_update_stripe, name='alertas-settings-stripe'),
    path('alertas/history/', views.DashboardHistoryView.as_view(), name='alertas-history'),

    path('alertas/history/download/<id>/', views.download_alerta_history_csv, name='alerta-history-download'),

#    url(r'^(?P<id>\d+)/$', views.alertas_view, name='alertas-detail'),

    # AJAX
    path('alertas/suggest_company/', views.suggest_company, name='suggest_company'),
    path('alertas/suggest_person/', views.suggest_person, name='suggest_person'),
    path('alertas/remove_card/', views.remove_card, name='remove_card'),
    path('alertas/set_default_card/', views.set_default_card, name='set_default_card'),

    path('ajax/empresa/follow', views.ajax_empresa_follow, name='borme-ajax-empresa-follow'),
]
