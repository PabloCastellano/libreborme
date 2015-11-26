from tastypie.resources import ModelResource
from borme.models import Company, Person


class CompanyResource(ModelResource):
    class Meta:
        queryset = Company.objects.all()
        resource_name = 'empresa'
        allowed_methods = ['get']
        excludes = ['date_updated']


class PersonResource(ModelResource):
    class Meta:
        queryset = Person.objects.all()
        resource_name = 'persona'
        allowed_methods = ['get']
        excludes = ['date_updated']
