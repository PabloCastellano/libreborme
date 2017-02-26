from django.contrib import admin
from . import models


class AlertaCompanyAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'is_enabled', 'send_html')
    list_filter = ('user',)
    search_fields = ['user', 'company', 'is_enabled']


class AlertaPersonAdmin(admin.ModelAdmin):
    list_display = ('user', 'person', 'is_enabled', 'send_html')
    list_filter = ('user',)
    search_fields = ['user', 'person', 'is_enabled']


class AlertaActoAdmin(admin.ModelAdmin):
    list_display = ('user', 'provincia', 'is_enabled', 'send_html')
    list_filter = ('user', 'send_html')
    search_fields = ['user', 'provincia', 'is_enabled']


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_type')
    list_filter = ('user', 'account_type')
    search_fields = ['user', 'account_type']


class LBInvoiceAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'end_date', 'amount', 'payment_type', 'is_paid')
    list_filter = ('user', 'payment_type')
    search_fields = ['user', 'payment_type', 'is_paid']


class AlertasConfigAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')
    search_fields = ['key']
    

admin.site.register(models.AlertaCompany, AlertaCompanyAdmin)
admin.site.register(models.AlertaPerson, AlertaPersonAdmin)
admin.site.register(models.AlertaActo, AlertaActoAdmin)
admin.site.register(models.Profile, ProfileAdmin)
admin.site.register(models.LBInvoice, LBInvoiceAdmin)
admin.site.register(models.AlertasConfig, AlertasConfigAdmin)