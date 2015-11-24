# Instalación

Estas instrucciones se han comprobado que funcionan en Ubuntu 14.04 32 bits. Para otras distribuciones el proceso debería ser similar.

Dependencias:

    sudo apt-get install python3-software-properties software-properties-common \
    build-essential python3-pip python3-dev python3-venv python3-wheel \
    python3-setuptools libxml2-dev libxslt1-dev libgmp-dev zlib1g-devsudo \
    nginx-full nginx-common uwsgi-plugin-python3 openssl supervisor checkinstall \
    wget git libpq-dev postgresql postgresql-contrib python-psycopg2 \
    openjdk-7-jre elasticsearch

    echo ". ~/.virtualenvs/libreborme/bin/activate" >> ~/.bashrc

Instalación de libreborme:

    git clone https://github.com/PabloCastellano/libreborme.git
    cd libreborme
    mkvirtualenv libreborme -p /usr/bin/python3
    pip install -r requirements/base.txt

Configuración de PostgreSQL:

    sudo su postgres
    psql template1 -c 'CREATE EXTENSION hstore;'
    psql -U postgres -c 'CREATE DATABASE libreborme;'
    psql -U postgres -c "CREATE USER libreborme WITH PASSWORD 'password';"
    psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE libreborme TO libreborme;"

Ajusta tu configuración en libreborme/settings.py con tus rutas y especialmente cambia la variable SECRET_KEY.

    ./manage.py migrate
    ./manage.py loaddata libreborme/fixtures/users.json
    Esto por defecto crea la cuenta `admin` con la contraseña `0000`.

## Ejecución

    cd libreborme
    ./manage.py runserver

## Herramientas de desarrollo

Si quieres instalar herramientas de desarrollo:

    pip install -r requirements/development.txt

## En producción:

    apt-get install nginx
    cd ~/libreborme
    workon libreborme
    ./manage.py collecstatic
    pip install -r requirements/production.txt
    mkdir /home/libreborme/run/
    chmod 775 /home/libreborme/run/
    adduser libreborme www-data

TODO: supervisor, uwsgi

# Comandos

    ./manage.py companyinfo "SOCIEDAD ESTATAL CORREOS Y TELEGRAFOS SA"
    ./manage.py companyinfo sociedad-estatal-correos-y-telegrafos
    ./manage.py findcompany correos asd
    ./manage.py importbormepdf /home/libreborme/.bormes/pdf/2009/01/02/BORME-A-2009-1-31.pdf -v 3

Para actualizar a la última versión:

    git stash && git pull && git stash pop && ./manage.py updateversion

Tests:

    ./runtests.sh

# Rellenar la BD con datos

LibreBorme usa la librería **bormeparser** para extraer la información de los archivos BORME.

    ./manage.py importborme -- --init local

# Tareas periódicas

LibreBorme usa cron para sincronizar diariamente los nuevos BORMEs.

    crontab -e

Añadir la siguiente línea al final

    0 8 * * 1-5     /var/www/libreborme/script.sh

El archivo script.sh debe tener el siguiente contenido:

    #!/bin/sh
    
    . ~/.virtualenvs/libreborme/bin/activate
    cd /var/www/libreborme && ./manage.py importbormetoday
