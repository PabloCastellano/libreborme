import logging
import os
import subprocess

import libreborme

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
logger.addHandler(ch)
logger.setLevel(logging.INFO)


def get_git_revision_short_hash():
    os.chdir(os.path.dirname(libreborme.__file__))
    try:
        version = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip()
        if isinstance(version, bytes):
            version = version.decode('unicode_escape')
    except subprocess.CalledProcessError:
        logger.warning("Couldn't guess git revision")
        version = 'Unknown'
    return version
