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

run:
		./manage.py runserver
