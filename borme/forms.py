from django import forms
from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from haystack.forms import SearchForm, model_choices


class LBSearchForm(SearchForm):
    def __init__(self, *args, **kwargs):
        super(LBSearchForm, self).__init__(*args, **kwargs)
        self.fields['models'] = forms.MultipleChoiceField(choices=model_choices(), required=False, label=_('Search In'), widget=forms.CheckboxSelectMultiple)

    def get_models(self):
        """Return an alphabetical list of model classes in the index."""
        search_models = []

        if self.is_valid():
            if 'type' not in self.cleaned_data or self.cleaned_data['type'] == 'all':
                search_models.append(apps.get_model('borme', 'Company'))
                search_models.append(apps.get_model('borme', 'Person'))
            else:
                search_models.append(apps.get_models('borme', self.cleaned_data['type'].capitalize()))

        return search_models

    def search(self):
        sqs = super(LBSearchForm, self).search()
        models = {'Person': [], 'Company': []}
        for model in self.get_models():
            models[model.__name__] = sqs.models(model)
        return models
