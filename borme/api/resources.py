from tastypie.resources import ModelResource
from borme.models import Company, Person


class CompanyResource(ModelResource):
    class Meta:
        queryset = Company.objects.all()
        allowed_methods = ['get']
        excludes = ['date_updated']


class PersonResource(ModelResource):
    class Meta:
        queryset = Person.objects.all()
        allowed_methods = ['get']
        excludes = ['date_updated']
