from django.contrib import admin
from . import models


class AlertaCompanyAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'send_html', 'is_enabled')
    list_filter = ('user', 'is_enabled')
    search_fields = ['user__username', 'user__email', 'company__name']


class AlertaPersonAdmin(admin.ModelAdmin):
    list_display = ('user', 'person', 'send_html', 'is_enabled')
    list_filter = ('user', 'is_enabled')
    search_fields = ['user__username', 'user__email', 'person__name']


class AlertaActoAdmin(admin.ModelAdmin):
    list_display = ('user', 'evento', 'periodicidad', 'provincia', 'send_html', 'is_enabled')
    list_filter = ('evento', 'periodicidad', 'send_html', 'is_enabled')
    search_fields = ['user__username', 'user__email', 'provincia']
    # TODO: get_provincia_display


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_type', 'notification_method', 'notification_email', 'notification_url')
    list_filter = ('notification_method', 'account_type')
    search_fields = ['user__username', 'user__email', 'notification_email', 'notification_url']


class LBInvoiceAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'end_date', 'amount', 'payment_type', 'is_paid')
    list_filter = ('is_paid', 'payment_type')
    search_fields = ['user__username', 'user__email']


class AlertasConfigAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')
    search_fields = ['key']


admin.site.register(models.AlertaCompany, AlertaCompanyAdmin)
admin.site.register(models.AlertaPerson, AlertaPersonAdmin)
admin.site.register(models.AlertaActo, AlertaActoAdmin)
admin.site.register(models.Profile, ProfileAdmin)
admin.site.register(models.LBInvoice, LBInvoiceAdmin)
admin.site.register(models.AlertasConfig, AlertasConfigAdmin)
