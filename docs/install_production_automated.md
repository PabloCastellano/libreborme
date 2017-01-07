# Instalación automatizada para producción

Esta sección describe cómo realizar una instalación de LibreBORME automatizada y en producción.

## Advertencia

> **Tanto este procedimiento como los playbooks de Ansible dejaron de ser mantenidos en marzo de 2016, por lo que seguramente no funcionará a día de hoy sin modificaciones. Se recomienda por tanto seguir la [instalación manual](installation).**

## Prerrequisitos

LibreBORME utiliza [Ansible](http://www.ansible.com/) para ser desplegado en un servidor remoto. 

Para instalar Ansible en tu máquina:

    sudo apt-get install software-properties-common
    sudo apt-add-repository ppa:ansible/ansible
    sudo apt-get update
    sudo apt-get install ansible

[Aquí](http://docs.ansible.com/intro_installation.html#latest-releases-via-apt-ubuntu) puedes consultar las instrucciones de instalación de Ansible más detalladas y para otras distribuciones.

La versión actual de Ansible no soporta Python 3, por lo que tu máquina remota deberá tener instalado el intérprete de Python 2. Asegúrate de que lo está instalando python-minimal:

    sudo apt-get install python-minimal

## Descargar libreborme-ansible

Descarga el archivo:

- tarball: [https://github.com/PabloCastellano/libreborme-ansible/tarball/master](https://github.com/PabloCastellano/libreborme-ansible/tarball/master)
- zip: [https://github.com/PabloCastellano/libreborme-ansible/archive/master.zip](https://github.com/PabloCastellano/libreborme-ansible/archive/master.zip)

Ejemplo:

    wget https://github.com/PabloCastellano/libreborme-ansible/archive/master.zip -O libreborme-ansible.zip
    unzip libreborme-ansible.zip
    rm libreborme-ansible.zip
    cd libreborme-ansible-master

Alternativamente también puedes usar Git:

    sudo apt-get install git
    git clone https://github.com/PabloCastellano/libreborme-ansible.git
    cd libreborme-ansible

# Despliegue 

A continuación necesitas tener acceso SSH al servidor con el usuario root o con un usuario en el grupo *sudo*. Cambia la IP y el usuario de tu host en el archivo *hosts*.

Solo debes ejecutar:

    ansible-playbook install.yml

Si no tienes acceso SSH con clave pública añade *--ask-pass*.

    ansible-playbook install.yml --ask-pass

# Actualización de una instancia existente

    ansible-playbook update.yml

Si hubiera cambios en el esquema de la base de datos hay que ejecutar también:

    ./manage.py migrate
