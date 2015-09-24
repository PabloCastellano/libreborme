import os
import subprocess

import libreborme


def get_git_revision_short_hash():
    os.chdir(os.path.dirname(libreborme.__file__))
    try:
        version = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip()
        if isinstance(version, bytes):
            version = version.decode('unicode_escape')
    except subprocess.CalledProcessError:
        # TODO: logging.warn()
        version = 'Unknown'
    return version
