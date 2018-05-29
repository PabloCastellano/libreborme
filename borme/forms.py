from django import forms
from django.utils.translation import ugettext_lazy as _

CHOICES = (('all', 'Todos'), ('company', 'Empresas'), ('person', 'Personas'),)


class LBSearchForm(forms.Form):
    q = forms.CharField(label=_('Nombre'), max_length=100)
    type = forms.ChoiceField(choices=CHOICES, required=False, label=_('Tipo'),
                             widget=forms.RadioSelect)

    # 25 results per page * 400 pages = 10000 results
    # Easy way to forbid searches that exceed default max results in
    # ElasticSearch. See index.max_result_window property
    page = forms.IntegerField(min_value=1, max_value=400)
