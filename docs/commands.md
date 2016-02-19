LibreBORME proporciona una serie de comandos de Django.

- **importborme** permite importar datos de BORMEs en lotes
- **importbormepdf** permite importar un archivo BORME en formato PDF
- **importbormejson** permite importar un archivo BORME en formato JSON
- **importbormetoday** importa los BORMEs del día actual.
   Este comando se ejecuta periódicamente mediante cron para incorporar los nuevos datos a LibreBORME
- **findperson** permite buscar personas en la base de datos
- **findcompany** permite buscar empresas en la base de datos
- **companyinfo** muestra información sobre la empresa especificada
- **personinfo** muestra información sobre la persona especificada
- **updateversion** actualiza datos internos de LibreBORME

## Importar datos

Una vez está funcionando la instancia de LibreBORME nos interesa llenarla de datos.
Este es un proceso largo debido a la gran cantidad de datos que se deben procesar.

En las pruebas realizadas importando 7 años de BORME (2009-2015), el proceso tardó más
de 5 días (125 horas) en indexar todos los datos en un servidor virtual con un núcleo y 1GB de RAM.
Con dos núcleos, el proceso de importación se redujo a 4 días.

Para comenzar la importación de datos desde cero, podemos ejecutar el comando importborme de la siguiente manera:

    ./manage.py importborme -- --init

El proceso de importación consiste en los siguientes pasos:

- Descargar sumario XML
- Obtener del sumario las URLs de los PDF
- Descargar archivos BORME PDF
- Extraer información de PDF
- Incorporar datos a PostgreSQL
- Reindexar los datos en Elasticsearch

Una vez finalizada la importación de datos es recomendable hacer una copia de las bases
de datos tanto de PostgreSQL como de Elasticsearch. De esta manera podemos restaurar los datos en
pocos minutos en vez de en días.
