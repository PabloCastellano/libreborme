# Instalación

Estas instrucciones se han comprobado que funcionan en Ubuntu 14.04 32 bits. Para otras distribuciones el proceso debería ser similar.

Dependencias:

    sudo apt-get install virtualenvwrapper
    sudo apt-get install libpq-dev postgresql postgresql-contrib
    sudo apt-get install libxml2-dev libxslt1-dev python-dev zlib1g-dev

    echo "export WORKON_HOME=$HOME/.virtualenvs" >> ~/.bashrc
    echo "source /usr/share/virtualenvwrapper/virtualenvwrapper.sh" >> ~/.bashrc
    source ~/.bashrc

Instalación de libreborme:

    git clone https://github.com/PabloCastellano/libreborme.git
    cd libreborme
    mkvirtualenv libreborme
    pip install -r requirements/base.txt
    cp libreborme/local_settings.py.example libreborme/local_settings.py

Ajusta tu configuración en libreborme/local_settings.py con tus rutas y especialmente cambia la variable SECRET_KEY.

    ./manage.py syncdb
    Puedes crear aquí tu superusuario o decir "no" y ejecutar:
    ./manage.py loaddata libreborme/fixtures/users.json
    Esto por defecto crea la cuenta `admin` con la contraseña `0000`.

## Ejecución

    source ~/.bash_aliases
    cd libreborme
    workon libreborme
    ./manage.py runserver --settings=libreborme.local_settings

### Opcional

Incluye el siguiente alias:

    echo "alias libreborme_run='workon libreborme && cd ~/libreborme && ./manage.py runserver --settings=libreborme.local_settings'" >> ~/.bash_aliases

y ejecuta simplemente:

    libreborme_run

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
    # Crear /etc/init.d/django-libreborme
    /etc/init.d/django-libreborme start
    update-rc.d django-libreborme defaults

# Comandos

    ./manage.py companyinfo "SOCIEDAD ESTATAL CORREOS Y TELEGRAFOS SA"
    ./manage.py companyinfo sociedad-estatal-correos-y-telegrafos
    ./manage.py findcompany correos asd
    ./manage.py importbormepdf /home/libreborme/.bormes/pdf/2009/01/02/BORME-A-2009-1-31.pdf -v 3

Para actualizar a la última versión:

    git stash && git pull && git stash pop && ./manage.py updateversion

Tests:

    ./manage.py test --settings=libreborme.local_settings

# Rellenar la BD con datos

LibreBorme usa la librería **bormeparser** para extraer la información de los archivos BORME.

    ./manage.py importborme -- --init local

TODO: cron sincronizador diario.
