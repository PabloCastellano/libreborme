from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from borme.models import get_borme_urls_from_slug
from borme.mixins import CacheMixin

import json


class IndexView(CacheMixin, LoginRequiredMixin, TemplateView):
    template_name = "index.html"


@csrf_exempt
@login_required
def dataremoval_search(request):
    data = json.loads(request.body.decode())

    q = data.get("query", "")
    step = data.get("step", 1)
    parameters = {}

    # TODO: document FTS - llamada a la propia API
    # TODO: Devolver JSON e iterar en JS

    urls = get_borme_urls_from_slug(q)
    if len(urls) == 0:
        return HttpResponse(status=400)

    if step == 1:
        parameters["HOST_BUCKET"] = settings.HOST_BUCKET
        parameters["nombre"] = q
        parameters["urls"] = urls

    template = get_template('email_template_{}.html'.format(step))
    response = template.render(parameters)

    return HttpResponse(response)
