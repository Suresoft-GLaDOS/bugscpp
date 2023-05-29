.PHONY: all install format lint test test-coverage test-taxonomy

default: test

readme:
	@PYTHONPATH=bugscpp/ python readme_generator.py README.rst.template

install:
	@pip install --upgrade pip
	@pip install -r requirements.txt

dev:
	@pip install --upgrade pip
	@pip install -r requirements.txt
	@pip install -r requirements_dev.txt

format:
	black .
	isort .

lint:
	flake8 . --config setup.cfg

test:
	@PYTHONPATH=bugscpp/ python -m pytest tests/ --ignore tests/taxonomy

test-fast:
	@PYTHONPATH=bugscpp/ python -m pytest tests/ --ignore tests/taxonomy --skip-slow

coverage:
ifeq ($(OS), Windows_NT)
	@set PYTHONPATH=bugscpp/
	python -m pytest tests/ \
		--cov-report=xml:reports/coverage/coverage.xml \
		--cov-report=html:reports/coverage \
		--cov=bugscpp \
		--ignore tests/taxonomy
else
	PYTHONPATH=bugscpp/ python -m pytest tests/ \
		--cov-report=xml:reports/coverage/coverage.xml \
		--cov-report=html:reports/coverage \
		--cov=bugscpp \
		--ignore tests/taxonomy
endif

test-taxonomy:
ifeq ($(OS), Windows_NT)
	@set PYTHONPATH=bugscpp/
	python -m pytest tests/taxonomy
else
	@PYTHONPATH=bugscpp/ python -m pytest tests/taxonomy
endif

all: install test
