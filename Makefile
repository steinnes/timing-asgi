setup:
	poetry install

test:
	poetry run pytest -s --cov-report term-missing --cov=statsd_asgi tests/


test_%:
	poetry run pytest -vsx tests -k $@ --pdb

lint:
	poetry run flake8 statsd_asgi/ tests/


clean:
	rm -rf dist/ pip-wheel-metadata *.egg-info
