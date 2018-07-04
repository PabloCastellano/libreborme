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


class LBInvoiceAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'end_date', 'amount', 'payment_type', 'is_paid')
    list_filter = ('is_paid', 'payment_type')
    search_fields = ['user__username', 'user__email']


class AlertasConfigAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')
    search_fields = ['key']


class AlertaHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'date', 'provincia', 'entidad', 'periodicidad')
    search_fields = ['user', 'date']


class LibrebormeLogsAdmin(admin.ModelAdmin):
    list_display = ('date', 'component', 'log', 'user')
    search_fields = ['date', 'component', 'log', 'user']


admin.site.register(models.AlertaCompany, AlertaCompanyAdmin)
admin.site.register(models.AlertaPerson, AlertaPersonAdmin)
admin.site.register(models.AlertaActo, AlertaActoAdmin)
admin.site.register(models.LBInvoice, LBInvoiceAdmin)
admin.site.register(models.AlertasConfig, AlertasConfigAdmin)
admin.site.register(models.AlertaHistory, AlertaHistoryAdmin)
admin.site.register(models.LibrebormeLogs, LibrebormeLogsAdmin)
