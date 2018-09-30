import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
logger.addHandler(ch)
logger.setLevel(logging.INFO)


def logger_acto(acto):
    logger.debug(acto.name)
    # logger.debug(acto.value)


def logger_anuncio_create(anuncio_id, company):
    logger.debug("Creando anuncio {}: {}".format(anuncio_id, company.fullname))


def logger_borme_create(cve):
    logger.debug("Creando borme {}".format(cve))


def logger_cargo(nombre_cargo, nombres):
    logger.debug("{} {} {}".format(nombre_cargo, nombres, len(nombres)))


def logger_empresa_create(empresa):
    logger.debug('Creando empresa ' + empresa)


def logger_empresa_similar(company, empresa, cve):
    logger.warn("[{cve}] WARNING: Empresa similar. Mismo slug: {0}\n"
                "[{cve}] {1}\n"
                "[{cve}] {2}\n"
                .format(company.slug, company.name, empresa, cve=cve))


def logger_persona_create(nombre):
    logger.debug("Creando persona: {}".format(nombre))


def logger_persona_similar(slug, name, nombre, cve):
    logger.warn("[{cve}] WARNING: Persona similar. Mismo slug: {0}\n"
                "[{cve}] {0}\n"
                "[{cve}] {1}\n"
                .format(slug, name, nombre, cve=cve))


def logger_resume_import(cve="X"):
    # TODO: --from date
    logger.error("[{cve}] Una vez arreglado, reanuda la importación:\n"
                 "[{cve}]   python manage.py importbormetoday local"
                 .format(cve=cve))
