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
		./manage.py createsuperuser --username admin --email pablo@anche.no
		./manage.py djstripe_sync_customers
		./manage.py djstripe_sync_plans_from_stripe


run:
		docker-compose up -d
		./manage.py runserver
		# --settings=...

shell:
		./manage.py shell_plus

import:
		./manage.py importborme -f 2018-03-13 -t 2018-03-13 --local-only
