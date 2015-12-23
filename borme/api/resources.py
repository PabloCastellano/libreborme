from django.conf.urls import url
from django.core.paginator import Paginator
from haystack.query import SearchQuerySet
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash
from borme.models import Company, Person
from .serializers import LibreBormeJSONSerializer

# FIXME: fullname
class CompanyResource(ModelResource):
    class Meta:
        queryset = Company.objects.all()
        resource_name = 'empresa'
        allowed_methods = ['get']
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
                bundle = self.search_dehydrate(bundle)
                objects.append(bundle)
        except:
            pass

        object_list = {
            'objects': objects,
        }

        self.log_throttled_access(request)
        return self.create_response(request, object_list)

    # HACK: Based on full_dehydrate
    def search_dehydrate(self, bundle, for_list=False):
        use_in = ['all', 'list' if for_list else 'detail']

        for field_name, field_object in self.fields.items():
            if field_name not in ('slug', 'name', 'resource_uri'):
                continue

            field_use_in = getattr(field_object, 'use_in', 'all')
            if callable(field_use_in):
                if not field_use_in(bundle):
                    continue
            else:
                if field_use_in not in use_in:
                    continue

            if getattr(field_object, 'dehydrated_type', None) == 'related':
                field_object.api_name = self._meta.api_name
                field_object.resource_name = self._meta.resource_name

            bundle.data[field_name] = field_object.dehydrate(bundle, for_list=for_list)

            method = getattr(self, "dehydrate_%s" % field_name, None)

            if method:
                bundle.data[field_name] = method(bundle)

        bundle = self.dehydrate(bundle)
        return bundle


class PersonResource(ModelResource):
    class Meta:
        queryset = Person.objects.all()
        resource_name = 'persona'
        allowed_methods = ['get']
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
                bundle = self.search_dehydrate(bundle)
                objects.append(bundle)
        except:
            pass


        object_list = {
            'objects': objects,
        }

        self.log_throttled_access(request)
        return self.create_response(request, object_list)

    # HACK: Based on full_dehydrate
    def search_dehydrate(self, bundle, for_list=False):
        use_in = ['all', 'list' if for_list else 'detail']

        for field_name, field_object in self.fields.items():
            if field_name not in ('slug', 'name', 'resource_uri'):
                continue

            field_use_in = getattr(field_object, 'use_in', 'all')
            if callable(field_use_in):
                if not field_use_in(bundle):
                    continue
            else:
                if field_use_in not in use_in:
                    continue

            if getattr(field_object, 'dehydrated_type', None) == 'related':
                field_object.api_name = self._meta.api_name
                field_object.resource_name = self._meta.resource_name

            bundle.data[field_name] = field_object.dehydrate(bundle, for_list=for_list)

            method = getattr(self, "dehydrate_%s" % field_name, None)

            if method:
                bundle.data[field_name] = method(bundle)

        bundle = self.dehydrate(bundle)
        return bundle
