from tastypie.resources import ModelResource
from borme.models import Company, Person


class CompanyResource(ModelResource):
    class Meta:
        queryset = Company.objects.all()
        allowed_methods = ['get']
        #fields = ['username', 'first_name', 'last_name', 'last_login']


class PersonResource(ModelResource):
    class Meta:
        queryset = Person.objects.all()
        allowed_methods = ['get']
        #fields = ['username', 'first_name', 'last_name', 'last_login']
        #excludes = ['email', 'password', 'is_active', 'is_staff', 'is_superuser']