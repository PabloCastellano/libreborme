#!/usr/bin/env python

from setuptools import setup, find_packages
import libreborme
import sys

version = libreborme.version


if sys.version_info[0] == 3:
    long_description = open('README.md', encoding='utf-8').read()
else:
    long_description = open('README.md').read()

setup(
    name='libreborme',
    version=version,
    description=libreborme.__doc__,
    long_description=long_description,
    author='Pablo Castellano',
    author_email='pablo@anche.no',
    license='GPLv3',
    url='https://github.com/PabloCastellano/libreborme',
    download_url='https://github.com/PabloCastellano/libreborme/releases',
    packages=find_packages(exclude=['docs', 'docs.*']),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
    ],
    scripts=['libreborme/bin/libreborme'],
    test_suite='runtests.runtests',
)
