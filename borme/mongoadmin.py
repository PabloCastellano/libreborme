from mongonaut.sites import MongoAdmin
from borme.models import Company, Borme, Person


class CompanyAdmin(MongoAdmin):
    list_fields = ('name', 'is_active')
    search_fields = ('name',)
    #prepopulated_fields = {"slug": ("name",)}
    #readonly_fields = ('slug',)


class PersonAdmin(MongoAdmin):
    list_fields = ('name', 'in_companies')
    search_fields = ('name',)
    #prepopulated_fields = {"slug": ("name",)}
    #readonly_fields = ('slug',)


class BormeAdmin(MongoAdmin):
    list_fields = ('filename')
    search_fields = ('filename', 'date', 'province')


Company.mongoadmin = CompanyAdmin()
Borme.mongoadmin = BormeAdmin()
Person.mongoadmin = PersonAdmin()
