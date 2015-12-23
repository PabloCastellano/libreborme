from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = "libreborme/index.html"


class CookiesView(TemplateView):
    template_name = "libreborme/cookies.html"
