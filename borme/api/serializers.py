import json
from django.core.serializers.json import DjangoJSONEncoder
from tastypie.serializers import Serializer


class LibreBormeJSONSerializer(Serializer):
    def to_json(self, data, options=None):
        options = options or {}

        data = self.to_simple(data, options)

        # hstore
        if 'in_companies' in data:
            data['in_companies'] = eval(data['in_companies'])
        if 'in_bormes' in data:
            data['in_bormes'] = eval(data['in_bormes'])
        if 'cargos_actuales' in data:
            data['cargos_actuales'] = eval(data['cargos_actuales'])
        if 'cargos_actuales_p' in data:
            data['cargos_actuales_p'] = eval(data['cargos_actuales_p'])
        if 'cargos_actuales_c' in data:
            data['cargos_actuales_c'] = eval(data['cargos_actuales_c'])
        if 'cargos_historial' in data:
            data['cargos_historial'] = eval(data['cargos_historial'])
        if 'cargos_historial_p' in data:
            data['cargos_historial_p'] = eval(data['cargos_historial_p'])
        if 'cargos_historial_c' in data:
            data['cargos_historial_c'] = eval(data['cargos_historial_c'])

        return json.dumps(data, cls=DjangoJSONEncoder, sort_keys=True)
