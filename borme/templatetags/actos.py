from django.template.defaulttags import register
import borme.parser.actos


constitucion_text = \
    ("Se constituye la empresa con fecha {fecha_anuncio} mediante "
     "escritura pública. La empresa se crea con un capital social inicial de "
     "{capital} Euros e inicia su actividad el {begin}. El domicilio social "
     "en el momento de su constitución se establece en {address}. "
     "La empresa indica que su actividad es {purpose}")


ampliacion_capital_text = \
    ("Con fecha {fecha_anuncio}, mediante la correspondiente escritura ha "
     "quedado incrito en el Registro Mercantil la ampliación de {capital} € "
     "del capital social de la empresa. Esta ampliación representa un "
     "{porcentaje:.2f} % de incremento del capital, quedando un capital "
     "social resultante de {resultante_suscrito}€.")


cambio_denominacion_text = \
    ("Con fecha {fecha_anuncio}, la sociedad cambia su denominación social "
     "{anterior} a la denominación {nueva}")


transformacion_text = \
    ("Con fecha {fecha_anuncio}, la sociedad cambia su denominación social "
     "{anterior} a la denominación {nueva}")


unipersonal_text = \
    ("Con fecha {fecha_anuncio} se inscribe en el Registro Mercantil la "
     "adquisición del carácter unipersonal de la sociedad, siendo el titular "
     "jurídico y formal de las acciones o participaciones societarias "
     "{socio_unico}")


@register.filter
def is_acto_cargo(val):
    return borme.parser.actos.is_acto_cargo(val)


@register.filter
def is_acto_cargo_entrante(val):
    return borme.parser.actos.is_acto_cargo_entrante(val)


@register.simple_tag
def acto_as_text(name, value, date):
    if borme.parser.actos.is_acto_cargo(name):
        raise ValueError("Do not use this function for act: " + name)

    if name == 'Constitución':
        if 'capital' in value:
            text = constitucion_text.format(fecha_anuncio=date, **value)
        else:
            text = value[name]
    elif name == 'Ampliación de capital':
        if 'capital' in value:
            diferencia = value['resultante_suscrito'] - value['capital']
            if diferencia > 0:
                porcentaje = value['capital'] / diferencia * 100
            else:
                porcentaje = 100
            text = ampliacion_capital_text.format(fecha_anuncio=date,
                                                  porcentaje=porcentaje,
                                                  **value)
        else:
            text = value[name]
    elif name == 'Cambio de denominación social':
        if 'anterior' in value:
            text = cambio_denominacion_text.format(fecha_anuncio=date, **value)
        else:
            text = value[name]
    elif name == 'Declaración de unipersonalidad':
        if 'socio_unico' in value:
            text = unipersonal_text.format(fecha_anuncio=date, **value)
        else:
            text = value[name]
    elif name == 'Sociedad unipersonal':
        if 'socio_unico' in value:
            text = unipersonal_text.format(fecha_anuncio=date, **value)
        else:
            text = value[name]
    elif name == 'Transformación de sociedad':
        if 'anterior' in value:
            text = transformacion_text.format(fecha_anuncio=date, **value)
        else:
            text = value[name]
    else:
        if 'value' in value:
            return value['value']
        else:
            return value[name]

    return text
