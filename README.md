Install
=======

```
cd libreborme
git clone git@github.com:PabloCastellano/libreborme_alertas.git alertas
```

En `settings.py` añadir alertas a `INSTALLED_APPS`:

```
LOGIN_REDIRECT_URL = '/alertas/'
LOGOUT_REDIRECT_URL = '/alertas/'
```

En `urls.py` añadir a `urlpatterns`:

url(r'', include('alertas.urls')),

TODO: static files

Cron (opción 1)
---------------

TODO: virtualenv

```
00 9    * * 1-5     libreborme    cd /home/libreborme && .. && ./manage.py send_notifications daily new
05 9    * * 1-5     libreborme    cd /home/libreborme && .. && ./manage.py send_notifications daily liq
10 9    * * 1-5     libreborme    cd /home/libreborme && .. && ./manage.py send_notifications daily con
15 9    * * 5       libreborme    cd /home/libreborme && .. && ./manage.py send_notifications weekly new
20 9    * * 5       libreborme    cd /home/libreborme && .. && ./manage.py send_notifications weekly liq
25 9    * * 5       libreborme    cd /home/libreborme && .. && ./manage.py send_notifications weekly con
30 9    1 * *       libreborme    cd /home/libreborme && .. && ./manage.py send_notifications monthly new
35 9    1 * *       libreborme    cd /home/libreborme && .. && ./manage.py send_notifications monthly liq
40 9    1 * *       libreborme    cd /home/libreborme && .. && ./manage.py send_notifications monthly con
```

Cron (opción 2)
---------------

```
0 9     * * 1-5     {{ libreborme_dir }}/cron_send_notifications_daily.sh
15 9    * * 5       {{ libreborme_dir }}/cron_send_notifications_weekly.sh
30 9    1 * *       {{ libreborme_dir }}/cron_send_notifications_monthly.sh
```

