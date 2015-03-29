from fabric.api import *


env.use_ssh_config = True
env.hosts = ['libreborme1']
env.abort_on_prompts = True
env.colorize_errors = True
env.reject_unknown_hosts = True


def prepare_deployment(branch_name):
    local('python manage.py test borme')
    local('python manage.py test libreborme')
    local('git add -p && git commit')
    local('git checkout master && git merge ' + branch_name)


def update_django_project():
    """ Updates the remote django project.
    """
    with cd('/home/libreborme/libreborme'):
        run('git pull')
        with prefix('workon libreborme'):
            run('pip install -r requirements.txt')
            run('./manage.py collectstatic --noinput --settings=libreborme.local_settings')


def restart_webserver():
    """ Restarts remote nginx and uwsgi.
    """
    sudo("service django-libreborme restart")
    sudo("/etc/init.d/nginx reload")


def deploy():
    """ Deploy Django Project.
    """
    update_django_project()
    restart_webserver()


def testlive():
    run("ls")
