
Instalación
-----------

Estas instrucciones se han comprobado que funcionan en Ubuntu 14.04 32 bits. Para otras distribuciones el proceso debería ser similar.

Dependencias:

    sudo apt-get install virtualenvwrapper
    sudo apt-get install mongodb
    sudo apt-get install libxml2-dev libxslt1-dev python-dev zlib1g-dev

    echo "export WORKON_HOME=$HOME/.virtualenvs" >> ~/.bashrc
    echo "source /usr/share/virtualenvwrapper/virtualenvwrapper.sh" >> ~/.bashrc
    source ~/.bashrc

Hack temporal:
en `~/.virtualenvs/libreborme/local/lib/python2.7/site-packages/mongodbforms/documentoptions.py`
comentar la línea:

    from django.db.models.options import get_verbose_name

Y añadir a continuación:

    from django.utils.text import camel_case_to_spaces as get_verbose_name

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
    ./manage.py importbormecsv borme_parser/csv/BORME-A-2014-196-14.pdf-cropped.pdf.1.txt.clean.txt.4c.csv
    ./manage.py importbormecsv borme_parser/csv/*.csv
    ./manage.py importbormejson borme_parser/json/*.json
    ./manage.py importbormebson borme_parser/bson/*.bson

Para actualizar a la última versión:
    git stash && git pull && git stash pop && ./manage.py updateversion

Tests:
    ./manage.py test --settings=libreborme.local_settings

Rellenando con datos la BD
--------------------------

    cd borme_parser
    mkdir xml
    ./getAllBormeXML.py 20150101
    mkdir pdf
    ./getPDFfromXML.py 20150101
    ./crop_borme.py pdf
    ./parserPDF.py pdfcrop
    ./cleanText.py txt
    ./parserText2CSV4c.py txt2
    ./manage.py importbormecsv borme_parser/csv/*.csv
