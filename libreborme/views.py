from django.shortcuts import render
from django.shortcuts import render_to_response

from django.views.generic import TemplateView

class IndexView(TemplateView):
    template_name = "index.html"
