from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from . import models as m


@admin.register(m.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_type', 'notification_method',
                    'notification_email', 'notification_url')
    list_filter = ('notification_method',)
    search_fields = ['user__username', 'user__email', 'notification_email',
                     'notification_url']


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
