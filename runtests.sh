#!/bin/sh
./manage.py test borme --settings=libreborme.settings_test
# python manage.py test borme.tests.test_person_model.TestPersonModel --settings=libreborme.settings_test
# python manage.py test borme.tests.test_company_model.TestCompanyModel --settings=libreborme.settings_test

# coverage
#coverage run --source='.' manage.py test myapp
#coverage html
#coverage run --source=netdiff runtests.py && coverage report
