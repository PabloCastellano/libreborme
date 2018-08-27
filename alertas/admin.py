from django.contrib import admin
from . import models as m

# TODO: SubscriptionInline in LBInvoiceAdmin
# from djstripe.models import Subscription


@admin.register(m.AlertaActo)
class AlertaActoAdmin(admin.ModelAdmin):
    list_display = ('user', 'evento', 'periodicidad', 'provincia', 'send_html', 'is_enabled')
    list_filter = ('evento', 'periodicidad', 'send_html', 'is_enabled')
    search_fields = ['user__username', 'user__email', 'provincia']
    # TODO: get_provincia_display


# class SubscriptionInline(admin.StackedInline):
#     model = Subscription
#     can_delete = False
#     verbose_name_plural = 'Subscription'
#     fk_name = 'id'


@admin.register(m.LBInvoice)
class LBInvoiceAdmin(admin.ModelAdmin):
    # inlines = (SubscriptionInline, )
    list_display = ('user', 'start_date', 'end_date', 'amount', 'payment_type', 'ip', 'subscription_id')
    list_filter = ('user', 'payment_type')
    search_fields = ['user__username', 'user__email']

    # def get_inline_instances(self, request, obj=None):
    #     if not obj:
    #         return list()
    #     return super(LBInvoiceAdmin, self).get_inline_instances(request, obj)


@admin.register(m.AlertasConfig)
class AlertasConfigAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')
    search_fields = ['key']


@admin.register(m.AlertaHistory)
class AlertaHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'date', 'provincia', 'entidad', 'periodicidad')
    search_fields = ['user', 'date']


@admin.register(m.LibrebormeLogs)
class LibrebormeLogsAdmin(admin.ModelAdmin):
    list_display = ('date', 'component', 'log', 'user')
    search_fields = ['date', 'component', 'log', 'user']


@admin.register(m.Follower)
class FollowerAdmin(admin.ModelAdmin):
    list_display = ('user', 'slug', 'type', 'date_created')
    search_fields = ['user', 'slug', 'type']
    # search_fields = ['user__username', 'user__email', 'person__name']
