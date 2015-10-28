from django.contrib import admin
from borme.models import Anuncio, BormeLog, Borme, Config, Company, Person


class AnuncioAdmin(admin.ModelAdmin):
    search_fields = ['id_anuncio', 'year']


class BormeAdmin(admin.ModelAdmin):
    search_fields = ['cve', 'province']


class BormeLogAdmin(admin.ModelAdmin):
    search_fields = ['borme__cve']


class CompanyAdmin(admin.ModelAdmin):
    search_fields = ['name']


class PersonAdmin(admin.ModelAdmin):
    search_fields = ['name']


admin.site.register(Anuncio, AnuncioAdmin)
admin.site.register(Borme, BormeAdmin)
admin.site.register(BormeLog, BormeLogAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Config)
