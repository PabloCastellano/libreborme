#!/bin/sh
python manage.py test borme.tests libreborme.tests --settings=libreborme.settings_test
#python manage.py test libreborme.tests borme.tests --settings=libreborme.settings_test
#python manage.py test app --testrunner=app.filename.NoDbTestRunner
#python manage.py test libreborme.tests

# coverage
#coverage run --source='.' manage.py test myapp
#coverage html
#coverage run --source=netdiff runtests.py && coverage report
