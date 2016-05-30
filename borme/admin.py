from django.contrib import admin
from borme.models import Anuncio, BormeLog, Borme, Config, Company, Person


class AnuncioAdmin(admin.ModelAdmin):
    list_display = ('id_anuncio', 'year', 'company', 'borme', 'total_actos')
    search_fields = ['id_anuncio', 'year']


class BormeAdmin(admin.ModelAdmin):
    list_display = ('cve', 'date', 'province', 'section', 'total_anuncios')
    search_fields = ['cve', 'province']


class BormeLogAdmin(admin.ModelAdmin):
    list_display = ('borme', 'path', 'date_created', 'date_updated', 'date_parsed', 'parsed')
    search_fields = ['borme__cve']


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'date_updated', 'in_bormes', 'anuncios', 'total_bormes', 'total_anuncios')
    search_fields = ['name']


class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_updated', 'in_companies', 'in_bormes', 'total_companies', 'total_bormes')
    search_fields = ['name']


admin.site.register(Anuncio, AnuncioAdmin)
admin.site.register(Borme, BormeAdmin)
admin.site.register(BormeLog, BormeLogAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Config)
