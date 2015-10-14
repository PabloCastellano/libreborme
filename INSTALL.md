
Instalación
-----------

Estas instrucciones se han comprobado que funcionan en Ubuntu 14.04 32 bits. Para otras distribuciones el proceso debería ser similar.

Dependencias:

    sudo apt-get install virtualenvwrapper
    sudo apt-get install libpq-dev postgresql postgresql-contrib
    sudo apt-get install libxml2-dev libxslt1-dev python-dev zlib1g-dev

    echo "export WORKON_HOME=$HOME/.virtualenvs" >> ~/.bashrc
    echo "source /usr/share/virtualenvwrapper/virtualenvwrapper.sh" >> ~/.bashrc
    source ~/.bashrc

TODO: postgresql

Instalación de libreborme:

    git clone https://github.com/PabloCastellano/libreborme.git
    cd libreborme
    mkvirtualenv libreborme
    pip install -r requirements/base.txt
    cp libreborme/local_settings.py.example libreborme/local_settings.py
    Ajusta tu configuración en libreborme/local_settings.py con tus rutas y especialmente cambia la variable SECRET_KEY
    ./manage.py syncdb
    Puedes crear aquí tu superusuario o decir "no" y ejecutar:
    ./manage.py loaddata libreborme/fixtures/users.json
    Esto por defecto crea la cuenta `admin` con la contraseña `0000`.

Si quieres instalar herramientas de desarrollo:
    pip install -r requirements/development.txt

En producción:

- Instalación manual: http://libreborme.readthedocs.org/es/latest/installation/
- Instalación automatizada: http://libreborme.readthedocs.org/es/latest/install_production_automated/

Opcional
--------

    echo "alias libreborme_run='workon libreborme && cd ~/libreborme && ./manage.py runserver --settings=libreborme.local_settings'" >> ~/.bash_aliases
    source ~/.bash_aliases

Ejecución
---------

    cd libreborme
    workon libreborme
    ./manage.py runserver --settings=libreborme.local_settings

o simplemente:

    libreborme_run

Comandos
--------

    ./manage.py companyinfo "SOCIEDAD ESTATAL CORREOS Y TELEGRAFOS SA"
    ./manage.py companyinfo sociedad-estatal-correos-y-telegrafos
    ./manage.py findcompany correos asd
    ./manage.py importbormepdf /home/libreborme/.bormes/pdf/2009/01/02/BORME-A-2009-1-31.pdf -v 3

Para actualizar a la última versión:
    git stash && git pull && git stash pop && ./manage.py updateversion

Tests:
    ./manage.py test --settings=libreborme.local_settings

Rellenar la BD con datos
------------------------

    ./manage.py importborme -- --init local
