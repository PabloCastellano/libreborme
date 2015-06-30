# Instalación

Estas instrucciones se han comprobado que funcionan en Ubuntu 14.04 32 bits. Para otras distribuciones el proceso debería ser similar.

Dependencias:

    sudo apt-get install virtualenvwrapper
    sudo apt-get install mongodb
    sudo apt-get install libxml2-dev libxslt1-dev python-dev zlib1g-dev

    echo "export WORKON_HOME=$HOME/.virtualenvs" >> ~/.bashrc
    echo "source /usr/share/virtualenvwrapper/virtualenvwrapper.sh" >> ~/.bashrc
    source ~/.bashrc

Hay que parchear manualmente *django-mongogeneric* y *django-mongodbforms* ya que el mantenedor no ha aceptado aún los Pull Requests:

- [django-mongogeneric issue #3](https://github.com/jschrewe/django-mongogeneric/pull/3)
- [django-mongodbforms issue #74](https://github.com/jschrewe/django-mongodbforms/pull/74)

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
    ./manage.py importbormecsv borme_parser/csv/BORME-A-2014-196-14.pdf-cropped.pdf.1.txt.clean.txt.4c.csv
    ./manage.py importbormecsv borme_parser/csv/*.csv
    ./manage.py importbormejson borme_parser/json/*.json
    ./manage.py importbormebson borme_parser/bson/*.bson

Para actualizar a la última versión:

    git stash && git pull && git stash pop && ./manage.py updateversion

Tests:

    ./manage.py test --settings=libreborme.local_settings

# Rellenando con datos la BD

LibreBorme usa la librería **bormeparser** para extraer la información de los archivos BORME.

    ./manage.py importborme pdf/BORME-A-2015-27-10.pdf

TODO: cron sincronizador diario.
