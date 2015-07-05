# Instalación automatizada para producción

Esta sección describe cómo realizar una instalación de LibreBORME automatizada y en producción.

## Prerrequisitos

LibreBORME utiliza [Ansible](http://www.ansible.com/) para ser desplegado en un servidor remoto. 

Para instalar Ansible en tu máquina:

    sudo apt-get install software-properties-common
    sudo apt-add-repository ppa:ansible/ansible
    sudo apt-get update
    sudo apt-get install ansible

[Aquí](http://docs.ansible.com/intro_installation.html#latest-releases-via-apt-ubuntu) puedes consultar las instrucciones de instalación de Ansible más detalladas y para otras distribuciones.

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

Si tienes acceso SSH con clave y acceso como usuario root solo debes ejecutar:

    ansible-playbook install_root.yml

Si no tienes tienes acceso como root:

    ansible-playbook install.yml

Si en cualquiera de los casos no tienes acceso SSH con clave añade *--ask-pass*.

    ansible-playbook install_root.yml --ask-pass

# Actualización de una instancia existente

TODO

    ansible-playbook update.yml
