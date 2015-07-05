import subprocess

def get_git_revision_short_hash():
    version = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip()
    if isinstance(version, bytes):
        version = version.decode('unicode_escape')
    return version
