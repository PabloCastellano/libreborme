from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from . import models as m

UserModel = get_user_model()


@admin.register(m.MailTemplate)
class MailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'plain_text', 'html_text')
    search_fields = ['name', 'description', 'plain_text', 'html_text']


@admin.register(m.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('profile', 'user_link', 'user_customer', 'user_email', 'user_first_name', 'user_last_name', 'provincia', 'newsletter_promotions', 'newsletter_features', 'has_tried_subscriptions')
    list_filter = ('provincia', 'has_api_enabled', 'has_tried_subscriptions')
    search_fields = ['user__email', 'notification_url']

    def profile(self, obj):
        return obj.user
    profile.short_description = 'Profile'

    def user_link(self, obj):
        content_type = ContentType.objects.get_for_model(UserModel)
        admin_user_view = 'admin:%s_%s_change' % (content_type.app_label, content_type.model)
        return mark_safe('<a href="{0}">{1}</a>'.format(reverse(admin_user_view, args=(obj.user.id,)), obj.user))
    user_link.short_description = 'User model'

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'E-Mail'

    def user_first_name(self, obj):
        return obj.user.first_name
    user_first_name.short_description = 'First name'

    def user_last_name(self, obj):
        return obj.user.last_name
    user_last_name.short_description = 'Last name'

    def user_customer(self, obj):
        admin_user_view = 'admin:djstripe_customer_change'
        stripe_id = obj.user.djstripe_customers.get().stripe_id
        customer_id = obj.user.djstripe_customers.get().id
        return mark_safe('<a href="{0}">{1}</a>'.format(reverse(admin_user_view, args=(customer_id,)), stripe_id))
    user_customer.short_description = 'Djstripe customer'
