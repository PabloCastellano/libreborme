from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.safestring import mark_safe

from . import models as m


@admin.register(m.MailTemplate)
class MailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'plain_text', 'html_text')
    search_fields = ['name', 'description', 'plain_text', 'html_text']


@admin.register(m.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('profile', 'user_link', 'user_email', 'user_first_name', 'user_last_name', 'provincia', 'newsletter_promotions', 'newsletter_features')
    list_filter = ('provincia', 'notification_method',)
    search_fields = ['user__username', 'user__email', 'notification_email',
                     'notification_url']

    def profile(self, obj):
        return obj.user
    profile.short_description = 'Profile'

    def user_link(self, obj):
        return mark_safe('<a href="{0}">{1}</a>'.format(reverse('admin:auth_user_change', args=(obj.user.id,)), obj.user))
    user_link.short_description = 'User model'

    def user_email(self, obj):
        return obj.user.email

    def user_first_name(self, obj):
        return obj.user.first_name

    def user_last_name(self, obj):
        return obj.user.last_name


class ProfileInline(admin.StackedInline):
    model = m.Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'profile')
    list_select_related = ('profile', )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
