build:
	docker-compose build

run:
	docker-compose up

test:
	docker-compose run --rm backend sh -c "python -Wa manage.py test --noinput $(path)"

test-shuffle: only in django 4.0 (update later)
	docker-compose run --rm backend sh -c "python -Wa manage.py test --shuffle"

lint:
	docker-compose run --rm backend sh -c "flake8"

start-project:
	docker-compose run --rm backend sh -c "django-admin startproject backend ."

create-app:
	docker-compose run --rm backend sh -c "python manage.py startapp $(name)"

makemigrations:
	docker-compose run --rm backend sh -c "python manage.py makemigrations"

migrate:
	docker-compose run --rm backend sh -c "python manage.py wait_for_db && python manage.py migrate"

createsuperuser:
	docker-compose run --rm backend sh -c "python manage.py createsuperuser"