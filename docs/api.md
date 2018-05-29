Advertencia
----------

> **La API de LibreBORME es totalmente funcional aunque aún se encuentra en fase experimental.**
> **Los endpoints, los parámetros aceptados y los datos devueltos pueden sufrir cambios en el futuro.**

API de LibreBORME
-----------------

LibreBORME ofrece una [API](https://es.wikipedia.org/wiki/Interfaz_de_programaci%C3%B3n_de_aplicaciones)
para que terceros puedan realizar consultas de forma automatizada e integrar los datos en sus aplicaciones.

Las URLs de los endpoints son similares a las usadas para navegar por la web:

Persona

- Web: https://libreborme.net/borme/persona/**xxx-xxx-xxx**
- API: https://libreborme.net/borme/api/v1/persona/**xxx-xxx-xxx**
- Esquema: [https://libreborme.net/borme/api/v1/persona/schema/](https://libreborme.net/borme/api/v1/persona/schema/)

Empresa

- Web: https://libreborme.net/borme/empresa/**xxx-xxx-xxx**
- API: https://libreborme.net/borme/api/v1/empresa/**xxx-xxx-xxx**
- Esquema: [https://libreborme.net/borme/api/v1/empresa/schema/](https://libreborme.net/borme/api/v1/empresa/schema/)

Búsqueda

- Web (Persona): https://libreborme.net/borme/search/?q=**xxx**&page=**1**&type=**person**
- API (Persona): https://libreborme.net/borme/api/v1/persona/search/?q=**xxx**&page=**1**
- Web (Empresa): https://libreborme.net/borme/search/?q=**xxx**&page=**1**&type=**company**
- API (Empresa): https://libreborme.net/borme/api/v1/empresa/search/?q=**xxx**&page=**1**
as respuestas se proporcionan en formato JSON y

Ejemplos
--------

A continuación se muestran algunos ejemplos de cómo realizar peticiones a la API con curl:

Buscar la empresa "Gowex Málaga" ([enlace](https://libreborme.net/borme/api/v1/empresa/search/?q=Gowex+Malaga&page=1)):

```
$ curl -s "https://libreborme.net/borme/api/v1/empresa/search/?q=Gowex+Malaga&page=1" | python -m json.tool
{
    "objects": [
        {
            "name": "GOWEX MALAGA",
            "resource_uri": "/borme/api/v1/empresa/gowex-malaga/",
            "slug": "gowex-malaga"
        }
    ]
}

```
Buscar la persona "Rodrigo Rato" ([enlace](https://libreborme.net/borme/api/v1/persona/search/?q=Rodrigo+Rato&page=1)):

```
$ curl -s "https://libreborme.net/borme/api/v1/persona/search/?q=Rodrigo+Rato&page=1" | python -m json.tool
{
    "objects": [
        {
            "name": "Rato Figaredo Rodrigo",
            "resource_uri": "/borme/api/v1/persona/rato-figaredo-rodrigo/",
            "slug": "rato-figaredo-rodrigo"
        },
        {
            "name": "De Rato Figaredo Rodrigo",
            "resource_uri": "/borme/api/v1/persona/de-rato-figaredo-rodrigo/",
            "slug": "de-rato-figaredo-rodrigo"
        },
        {
            "name": "De Rato Y Figaredo Rodrigo",
            "resource_uri": "/borme/api/v1/persona/de-rato-y-figaredo-rodrigo/",
            "slug": "de-rato-y-figaredo-rodrigo"
        }
    ]
}
```

Como vemos, aparecen tres aunque todo apunta a que es la misma persona. Esto es debido a que el Registro Mercantil Central no da un identificador único por persona y publica
muchos datos de forma no estandarizada.


Consultar los datos de la persona "Rodrigo de Rato Figaredo" ([enlace](https://libreborme.net/borme/api/v1/persona/de-rato-figaredo-rodrigo/)):

```
$ curl -s "https://libreborme.net/borme/api/v1/persona/de-rato-figaredo-rodrigo/" | python -m json.tool
{
    "cargos_actuales": [
        {
            "date_from": "2009-01-19",
            "name": "Algaenergy SA",
            "title": "Consejero"
        },
        {
            "date_from": "2009-04-03",
            "name": "Rodanman Gestion 3 SL",
            "title": "Apoderado"
        },
        {
            "date_from": "2009-04-06",
            "name": "Rafi SL",
            "title": "Apoderado"
        },
        {
            "date_from": "2009-07-03",
            "name": "Criteria Caixacorp SA",
            "title": "MRO.COMS.EJE"
        },
[...]
    "date_updated": "2014-10-14",
    "in_bormes": [
        {
            "cve": "BORME-A-2009-11-28",
            "url": "https://boe.es/borme/dias/2009/01/19/pdfs/BORME-A-2009-11-28.pdf"
        },
        [...]
    ],
    "in_companies": [
        "Algaenergy SA",
        "Rodanman Gestion 3 SL",
        "Rafi SL",
        "Criteria Caixacorp SA",
        "Paracuga SL",
        "Arada SL",
        "Manita SL",
        "Proina SL",
        "Iberia Lineas Aereas De Espa\u00f1a SA",
        "Explotaciones De Caraba\u00f1a SL",
        "Corporacion Financiera Caja De Madrid SA",
        "Caja Madrid Cibeles SA",
        "Altae Banco SA",
        "Caja De Ahorros Y Monte De Piedad De Madrid ",
        "Banco Financiero Y De Ahorros SA",
        "Bankia SA",
        "Bankia Banca Privada SA",
        "Confederacion Espa\u00f1ola De Cajas De Ahorros ",
        "Garanair SL"
    ],
    "name": "De Rato Figaredo Rodrigo",
    "resource_uri": "/borme/api/v1/persona/de-rato-figaredo-rodrigo/",
    "slug": "de-rato-figaredo-rodrigo"
}
```
