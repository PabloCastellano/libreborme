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
    list_filter = ('user',)
    search_fields = ['user', 'provincia', 'is_enabled']


admin.site.register(models.AlertaCompany, AlertaCompanyAdmin)
admin.site.register(models.AlertaPerson, AlertaPersonAdmin)
admin.site.register(models.AlertaActo, AlertaActoAdmin)
