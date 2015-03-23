from django.template.defaulttags import register


# http://stackoverflow.com/a/8000091
@register.filter
def get_item(object, attribute):
    return object.__getattribute__(attribute)
    #return dictionary.get(key)
