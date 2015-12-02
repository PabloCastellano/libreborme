from django.conf.urls import url
from django.core.paginator import Paginator
from haystack.query import SearchQuerySet
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash
from borme.models import Company, Person
from .serializers import LibreBormeJSONSerializer


class CompanyResource(ModelResource):
    class Meta:
        queryset = Company.objects.all()
        resource_name = 'empresa'
        allowed_methods = ['get']
        serializer = LibreBormeJSONSerializer(formats=['json'])


class SearchCompanyResource(ModelResource):
    class Meta:
        queryset = Company.objects.all()
        resource_name = 'empresa'
        allowed_methods = ['get']
        fields = ['name', 'slug']  # TODO: fullname
        serializer = LibreBormeJSONSerializer(formats=['json'])

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/search%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_search'), name="api_get_search_company"),
        ]

    def get_search(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        # Do the query.
        sqs = SearchQuerySet().models(Company).load_all().auto_query(request.GET.get('q', ''))
        paginator = Paginator(sqs, 20)

        objects = []

        try:
            page = paginator.page(int(request.GET.get('page', 1)))

            for result in page.object_list:
                bundle = self.build_bundle(obj=result.object, request=request)
                bundle = self.full_dehydrate(bundle)
                objects.append(bundle)
        except:
            pass

        object_list = {
            'objects': objects,
        }

        self.log_throttled_access(request)
        return self.create_response(request, object_list)


class PersonResource(ModelResource):
    class Meta:
        queryset = Person.objects.all()
        resource_name = 'persona'
        allowed_methods = ['get']
        serializer = LibreBormeJSONSerializer(formats=['json'])


class SearchPersonResource(ModelResource):
    class Meta:
        queryset = Person.objects.all()
        resource_name = 'persona'
        allowed_methods = ['get']
        fields = ['name', 'slug']
        serializer = LibreBormeJSONSerializer(formats=['json'])

    def dehydrate_name(self, bundle):
        return bundle.data['name'].title()

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/search%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_search'), name="api_get_search_person"),
        ]

    def get_search(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        # Do the query.
        sqs = SearchQuerySet().models(Person).load_all().auto_query(request.GET.get('q', ''))
        paginator = Paginator(sqs, 20)

        objects = []

        try:
            page = paginator.page(int(request.GET.get('page', 1)))

            for result in page.object_list:
                bundle = self.build_bundle(obj=result.object, request=request)
                bundle = self.full_dehydrate(bundle)
                objects.append(bundle)
        except:
            pass


        object_list = {
            'objects': objects,
        }

        self.log_throttled_access(request)
        return self.create_response(request, object_list)
