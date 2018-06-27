from django.contrib import admin
from . import models as m


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_type', 'notification_method',
                    'notification_email', 'notification_url')
    list_filter = ('notification_method', 'account_type')
    search_fields = ['user__username', 'user__email', 'notification_email',
                     'notification_url']


admin.site.register(m.Profile, ProfileAdmin)
