from django.shortcuts import render
from django.shortcuts import render_to_response

from django.views.generic import TemplateView

class IndexView(TemplateView):
    template_name = "libreborme/index.html"


class Error404View(TemplateView):
    template_name = "libreborme/404.html"
