## Suscripciones

(solo soportado para PARSER=yabormeparser)

Se pueden generar con

./manage.py gen_subscriptions <event> FILE [FILE ...]

Por ejemplo

./manage.py gen_subscription -o yes adm /home/pablo2/yabormep/2018/03/13/*.json

E importarlo directamente

./manage.py gen_subscription --import adm /home/pablo2/yabormep/2018/03/13/*.json

O importarlo desde los archivos generados antes:

./manage.py import_subscription /home/pablo2/yabormep/2018/03/13/*_adm.json

Una vez están en la DB podemos enviarlas:

./manage.py send_subscriptions adm --email pablo@anche.no -v 3
./manage.py send_subscriptions
