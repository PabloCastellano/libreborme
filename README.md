Plataforma web para la consulta y el análisis del Boletín Oficial del Registro Mercantil

Concurso
--------

Este proyecto participa en el [Certamen de Proyectos Libres de la UGR](http://osl.ugr.es/2014/09/26/premios-a-proyectos-libres-de-la-ugr/) [(Bases)](http://osl.ugr.es/bases-de-los-premios-a-proyectos-libres-de-la-ugr/).

Instalación
-----------

    git clone https://github.com/PabloCastellano/libreborme.git
    cd libreborme
    mkvirtualenv libreborme
    sudo apt-get install mongodb
    sudo apt-get install libxml2-dev libxslt1-dev python-dev
    pip install -r requirements.txt
    ./manage.py syncdb
    ./manage.py migrate?
    ./manage.py loaddata libreborme/fixtures/users.json

Por defecto crea la cuenta `admin` con la contraseña `0000`.

Ejecución
---------

    cd libreborme
    workon libreborme
    ./manage.py runserver --settings=libreborme.local_settings

Comandos
--------

    ./manage.py companyinfo "SOCIEDAD ESTATAL CORREOS Y TELEGRAFOS SA"
    ./manage.py companyinfo sociedad-estatal-correos-y-telegrafos
    ./manage.py findcompany correos asd

