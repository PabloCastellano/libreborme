index:
		./manage.py search_index --models borme.Company --populate
		./manage.py search_index --models borme.Person --populate

reindex:
		./manage.py search_index --delete
		# the index must be created outside Django
		./manage.py search_index --models borme.Company --populate
		./manage.py search_index --models borme.Person --populate

robotstxt:
		./manage.py regenerate_robotstxt

backups:
		s3cmd ls s3://libreborme-prod/backups/database/

recreate_db:
		./manage.py reset_db --noinput
		./manage.py migrate
		./manage.py loaddata ./libreborme/fixtures/config.json
		./manage.py loaddata ./alertas/fixtures/alertasconfig.json
		# ./manage.py createsuperuser --username admin --email pablo@anche.no
		./manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'pablo@anche.no', '000000')"
		./manage.py djstripe_sync_customers
		./manage.py djstripe_sync_plans_from_stripe

run:
		docker-compose up -d
		./manage.py migrate
		./manage.py runserver --settings libreborme.settings_dev
		# ./manage.py runserver_plus
		# --settings=...

shell:
		./manage.py shell_plus --settings libreborme.settings_dev

import:
		./manage.py importborme -f 2018-03-13 -t 2018-03-13 --local-only

import1:
		./manage.py importbormejson /home/pablo2/.bormes/json/2018/03/13/BORME-A-2018-51-03.json

import2:
		./manage.py importbormejson /tmp/bpdf3/BORME-A-2018-51-03.json

emailserver:
		./manage.py mail_debug

graph_model:
		# ./manage.py graph_models -a -g -o graph_model.png
		./manage.py graph_models borme libreborme alertas -g -o graph_model.png
		@echo "Generated graph_model.png"

test:
		DJANGO_SETTINGS_MODULE=libreborme.settings_ci DB_HOST=localhost ./manage.py test -v 3

test1:
		DJANGO_SETTINGS_MODULE=libreborme.settings_ci DB_HOST=localhost ./manage.py test -v 3 borme.tests.test_import.TestImport2.test_nombramientos_ceses

test2:
		./setup.py test

test3:
		./runtests.py
