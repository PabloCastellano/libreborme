#!/bin/sh
python manage.py test borme.tests libreborme.tests --settings=libreborme.settings_test

# coverage
#coverage run --source='.' manage.py test myapp
#coverage html
#coverage run --source=netdiff runtests.py && coverage report
