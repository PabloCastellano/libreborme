from borme.models import Company, Person
from tastypie.resources import ModelResource
from .serializers import LibreBormeJSONSerializer


class CompanyResource(ModelResource):
    class Meta:
        queryset = Company.objects.all()
        resource_name = 'empresa'
        allowed_methods = ['get']
        serializer = LibreBormeJSONSerializer(formats=['json'])


class PersonResource(ModelResource):
    class Meta:
        queryset = Person.objects.all()
        resource_name = 'persona'
        allowed_methods = ['get']
        serializer = LibreBormeJSONSerializer(formats=['json'])
