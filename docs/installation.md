# Instalación manual

Estas instrucciones se han comprobado que funcionan en **Ubuntu 16.04 64 bits**. Para otras distribuciones el proceso debería ser similar.

Instalación de las dependencias:

    sudo apt-get install python3-software-properties software-properties-common \
    build-essential python3-pip python3-dev python3-venv python3-wheel \
    python3-setuptools libxml2-dev libxslt1-dev libgmp-dev zlib1g-dev \
    wget git libpq-dev postgresql postgresql-contrib python-psycopg2 \
    openssl checkinstall openjdk-8-jre elasticsearch

    echo ". ~/.virtualenvs/libreborme/bin/activate" >> ~/.bashrc

Configuración de PostgreSQL:

Creamos un usuario y una base de datos para LibreBOR:

    sudo su postgres
    psql -U postgres -c 'CREATE DATABASE libreborme;'
    psql -U postgres -c "CREATE USER libreborme WITH PASSWORD 'password';"
    psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE libreborme TO libreborme;"

Instalación de LibreBOR:

En este caso la instalación la realizamos en la carpeta /var/www/libreborme pero podría
ser cualquier otra teniendo en cuenta que tenemos que cambiar esta ruta en otros archivos de
configuración que la usan. Nos descargamos el paquete de LibreBOR y lo instalamos en
un entorno virtual de Python junto a sus dependencias (entre ellas, bormeparser):

    git clone https://github.com/PabloCastellano/libreborme.git
    cd libreborme
    mkvirtualenv libreborme -p /usr/bin/python3
    pip install -r requirements/base.txt

A continuación ajusta tu configuración en libreborme/settings.py con tus rutas y especialmente cambia
la variable SECRET_KEY.

Ya podemos crear el esquema de las tablas en la base de datos PostgreSQL y
cargar unos datos predefinidos necesarios para que funcione LibreBOR:

    ./manage.py migrate
    ./manage.py loaddata libreborme/fixtures/config.json
    ./manage.py collectstatic

## Ejecución

LibreBOR ya está listo para funcionar. Ejecutamos el servidor de desarrollo de Django para comprobarlo:

    cd libreborme
    ./manage.py runserver

## Herramientas de desarrollo

Si quieres instalar herramientas de desarrollo:

    pip install -r requirements/development.txt

## Versión en producción:

Si queremos la versión de producción necesitamos configurar además nginx, uwsgi y supervisor.

    sudo apt-get install nginx-full nginx-common uwsgi-plugin-python3 supervisor

Para configurar supervisor crearemos el archivo /etc/supervisor/conf.d/uwsgi.conf con el
siguiente contenido:

    [program:uwsgi]
    user=www-data
    directory=/var/www/libreborme
    command=uwsgi --ini uwsgi.ini --plugin python3
    autostart=true
    autorestart=true
    stopsignal=INT
    redirect_stderr=true
    stdout_logfile=/var/www/libreborme/log/uwsgi.log
    stdout_logfile_maxbytes=30MB
    stdout_logfile_backups=5

De esta forma supervisor monitorizará el proceso uwsgi y lo arrancará si el servidor se reinicia.
La interfaz uwsgi la configuramos creando el archivo /var/www/libreborme/uwsgi.ini con el siguiente contenido:

    [uwsgi]
    chdir=/var/www/libreborme
    module=mylibreborme.wsgi:application
    master=True
    pidfile=/var/www/libreborme/uwsgi.pid
    socket=libreborme.sock
    chmod-socket = 664
    processes=2
    harakiri=20
    max-requests=5000
    vacuum=True
    home=/home/libreborme/.virtualenvs/libreborme
    enable-threads=True
    env=HTTPS=on
    buffer-size=8192

Por último nos queda configurar en nginx un nuevo sitio web creando el archivo /etc/nginx/sites-available/libreborme
con el siguiente contenido:

    server {
      listen 80;

      server_name librebor.me;

      access_log /var/log/nginx/libreborme.access.log;
      error_log /var/log/nginx/libreborme.error.log;

      root /var/www/libreborme/public_html;
      index index.html index.htm;

      # set client body size #
      client_max_body_size 5M;

      location @uwsgi {
        uwsgi_pass unix:/var/www/libreborme/libreborme.sock;
        include uwsgi_params;
        uwsgi_param HTTP_X_FORWARDED_PROTO https;
      }

      location / {
        try_files $uri @uwsgi;
      }

      location /static {
        alias /var/www/libreborme/mylibreborme/static/;
      }

      location ~ /\.ht {
        deny all;
      }
    }

Y activamos el sitio:

    sudo ln -sf /etc/nginx/sites-available/libreborme /etc/nginx/sites-enabled/libreborme
    sudo supervisorctl restart uwsgi
    sudo service nginx restart

## Tareas periódicas

Queremos que cada día LibreBOR descargue los nuevos BORMEs y actualice la base
de datos con los últimos cambios en el Registro Mercantil. Para ello vamos a configurar
una tarea programada de cron. Creamos el archivo /var/www/libreborme/script.sh con el
siguiente contenido, al que le daremos también permisos de ejecución:

    #!/bin/sh
    . ~/.virtualenvs/libreborme/bin/activate

    cd /var/www/libreborme && ./manage.py importbormetoday

El archivo necesita permisos de ejecución:

    chmod 755 /var/www/libreborme/script.sh

Finalmente añadimos la tarea programada con la utilidad crontab y la configuramos para
que se ejecute de lunes a viernes (1-5) a las 8:00 AM:

    crontab -e

    # Añadir la siguiente línea al final del archivo:
    0 8 * * 1-5

# Comandos

    ./manage.py companyinfo "SOCIEDAD ESTATAL CORREOS Y TELEGRAFOS SA"
    ./manage.py companyinfo sociedad-estatal-correos-y-telegrafos
    ./manage.py findcompany correos asd
    ./manage.py importbormepdf /home/libreborme/.bormes/pdf/2009/01/02/BORME-A-2009-1-31.pdf -v 3

Para actualizar a la última versión:

    git stash && git pull && git stash pop && ./manage.py updateversion

Tests:

    ./runtests.sh
