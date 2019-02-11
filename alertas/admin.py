from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _

from . import models as m
from libreborme import models as lb_models

# TODO: SubscriptionInline in LBInvoiceAdmin
# from djstripe.models import Subscription


@admin.register(m.AlertaActo)
class AlertaActoAdmin(admin.ModelAdmin):
    list_display = ('user', 'evento', 'periodicidad', 'provincia', 'is_enabled', 'stripe_subscription', 'created_at')
    list_filter = ('evento', 'periodicidad', 'is_enabled')
    search_fields = ['user__email', 'provincia']
    # TODO: get_provincia_display


# class SubscriptionInline(admin.StackedInline):
#     model = Subscription
#     can_delete = False
#     verbose_name_plural = 'Subscription'
#     fk_name = 'id'


"""
@admin.register(m.LBInvoice)
class LBInvoiceAdmin(admin.ModelAdmin):
    # inlines = (SubscriptionInline, )
    list_display = ('user', 'start_date', 'end_date', 'amount', 'payment_type', 'ip', 'subscription_id')
    list_filter = ('user', 'payment_type')
    search_fields = ['user__email']

    # def get_inline_instances(self, request, obj=None):
    #     if not obj:
    #         return list()
    #     return super(LBInvoiceAdmin, self).get_inline_instances(request, obj)
"""


class ProfileInline(admin.StackedInline):
    model = lb_models.Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


@admin.register(m.User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'profile')
    list_select_related = ('profile', )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    inlines = (ProfileInline, )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(UserAdmin, self).get_inline_instances(request, obj)


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
    # search_fields = ['user__email', 'person__name']
