import subprocess


def get_git_revision_short_hash():
    try:
        version = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip()
        if isinstance(version, bytes):
            version = version.decode('unicode_escape')
    except subprocess.CalledProcessError:
        # TODO: logging.warn()
        version = 'Unknown'
    return version
