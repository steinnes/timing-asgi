setup:
	poetry install

test:
	poetry run pytest -s --cov-report term-missing --cov=timing_asgi tests/


test_%:
	poetry run pytest -vsx tests -k $@ --pdb

lint:
	poetry run flake8 timing_asgi/ tests/

black:
	poetry run black $(shell git diff --name-only --diff-filter d HEAD|grep \.py$)


clean:
	rm -rf dist/ pip-wheel-metadata *.egg-info
