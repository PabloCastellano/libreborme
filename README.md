![logo libreborme](libreborme/static/libreborme_logo.png)

[![Travis libreborme](https://travis-ci.org/PabloCastellano/libreborme.svg?branch=master)](https://travis-ci.org/PabloCastellano/libreborme)
[![Coverage Status](https://coveralls.io/repos/PabloCastellano/libreborme/badge.svg?branch=master&service=github)](https://coveralls.io/github/PabloCastellano/libreborme?branch=master)
[![Documentation Status](https://readthedocs.org/projects/libreborme/badge/?version=latest)](https://readthedocs.org/projects/libreborme/?badge=latest)
[![Requirements Status](https://requires.io/github/PabloCastellano/libreborme/requirements.svg?branch=master)](https://requires.io/github/PabloCastellano/libreborme/requirements/?branch=master)

En estos momentos hay una versión en producción en https://libreborme.net.

Acerca de LibreBORME
----------------

LibreBORME es una plataforma web para la consulta y el análisis del Boletín Oficial del Registro Mercantil.

LibreBORME nace en 2014 como un Proyecto de Fin de Carrera con la intención de «abrir» los datos del Registro Mercantil de España.
Aprovechando que [desde 2009](http://elpais.com/diario/2008/01/03/ciberpais/1199330666_850215.html)
se publica el BORME en formato electrónico, LibreBORME utiliza la librería [bormeparser](https://github.com/PabloCastellano/bormeparser/)
para *leérselo* por ti cada mañana y añadir a su base de datos los últimos cambios. De esta manera tú puedes hacer búsquedas semánticas,
recibir notificaciones y usar estos datos de manera sencilla y para lo que quieras.

Para más información puedes leer las siguientes entradas en el blog del autor:
- [Qué es LibreBORME](https://pablog.me/blog/2015/02/que-es-libreborme/) - [What is LibreBORME](https://pablog.me/que-es-libreborme-en.html) (25 de febrero de 2015)
- [Versión online de LibreBORME](https://pablog.me/blog/2015/03/version-online-de-libreborme/) (31 de marzo de 2015)
- [LibreBORME tercer premio en el I Certamen de Proyectos Libres de la UGR](https://pablog.me/blog/2015/07/libreborme-tercer-premio-en-el-i-certamen-de-proyectos-libres-de-la-ugr/) (15 de julio de 2015)

Y en los siguientes medios:
- [LibreBORME, la herramienta gratuita para investigar empresas españolas desde casa](http://www.elconfidencial.com/tecnologia/2016-02-14/libreborme-la-herramienta-gratuita-para-investigar-empresas-espanolas-desde-casa_1151596/) (El Confidencial, 14 de febrero de 2016)

LibreBORME participó en el [I Certamen de Proyectos Libres de la UGR](http://osl.ugr.es/2014/09/26/premios-a-proyectos-libres-de-la-ugr/) [(Bases)](http://osl.ugr.es/bases-de-los-premios-a-proyectos-libres-de-la-ugr/) donde obtuvo el tercer premio.

Instalación
-----------

Para instrucciones de cómo montar tu propia instancia de LibreBORME, echa un vistazo a [INSTALL.md](INSTALL.md).

Documentación
-------------

La documentación más actualizada del proyecto se encuentra disponible en [https://libreborme.readthedocs.org/es/develop/](https://libreborme.readthedocs.org/es/develop/).

Es posible generarla localmente mediante mkdocs:

    pip install -r requirements/docs.txt
    mkdocs build

Contribuciones
--------------

Si deseas contribuir al proyecto puedes enviarme tus Pull Requests en GitHub, donde también
puedes ojear el [listado de bugs](https://github.com/PabloCastellano/libreborme/issues).

Donaciones
----------

Si quieres apoyar económicamente el proyecto puedes hacerlo a través de [PayPal](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=contacto%40libreborme%2enet&lc=ES&item_name=LibreBORME&item_number=Servicio%20web&currency_code=EUR&bn=PP%2dDonationsBF%3abtn_donate_LG%2egif%3aNonHosted) o Bitcoin en la dirección [1Jp6SdEvPWahE5cDQ61StroCRM6Sbvxz94](https://blockchain.info/address/1Jp6SdEvPWahE5cDQ61StroCRM6Sbvxz94).

Licencia
--------

LibreBORME es software libre y su código fuente está accesible en [GitHub](https://github.com/PabloCastellano/libreborme) bajo la licencia [Affero GPL v3](https://www.gnu.org/licenses/agpl-3.0.html).

© Desarrolladores de LibreBORME. Véase el archivo [AUTHORS](AUTHORS).
