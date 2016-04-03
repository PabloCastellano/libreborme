from django.views.decorators.cache import cache_page


# https://gist.github.com/cyberdelia/1231560
class CacheMixin(object):
    cache_timeout = 3600

    def get_cache_timeout(self):
        return self.cache_timeout

    def dispatch(self, *args, **kwargs):
        return cache_page(self.get_cache_timeout())(super(CacheMixin, self).dispatch)(*args, **kwargs)
