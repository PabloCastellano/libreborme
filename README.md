Install
=======

settings.py:

Añadir alertas a INSTALLED_APPS 

LOGIN_REDIRECT_URL = '/alertas/'
LOGOUT_REDIRECT_URL = '/alertas/'


urls.py:

Añadir a urlpatterns:

url(r'', include('alertas.urls')),
