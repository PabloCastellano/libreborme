from django.contrib import admin
from .models import CompanyRobotsTxt, PersonRobotsTxt


@admin.register(CompanyRobotsTxt)
class CompanyRobotsTxtAdmin(admin.ModelAdmin):
    list_display = ('company', 'get_slug', 'date_created', 'date_updated')
    list_filter = ('date_created',)
    search_fields = ['company__name']
    raw_id_fields = ('company',)

    def get_slug(self, instance):
        return instance.company.slug
    get_slug.short_description = 'Slug'
    get_slug.admin_order_field = 'company__name'


@admin.register(PersonRobotsTxt)
class PersonRobotsTxtAdmin(admin.ModelAdmin):
    list_display = ('person', 'get_slug', 'date_created', 'date_updated')
    list_filter = ('date_created',)
    search_fields = ['person__name']
    raw_id_fields = ('person',)

    def get_slug(self, instance):
        return instance.person.slug
    get_slug.short_description = 'Slug'
    get_slug.admin_order_field = 'person__name'
