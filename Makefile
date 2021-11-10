.PHONY: all install format lint test test-coverage test-taxonomy

default: test

install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

format:
	black .
	isort .

lint:
	flake8 . --config setup.cfg

test:
	@PYTHONPATH=defects4cpp/ python3 -m pytest \
		--ignore tests/taxonomy

coverage:
	@PYTHONPATH=defects4cpp/ python3 -m pytest \
		--cov-report=xml:reports/coverage/coverage.xml \
		--cov-report=html:reports/coverage \
		--cov=defects4cpp \
		--ignore tests/taxonomy

test-taxonomy:
	@PYTHONPATH=defects4cpp/ python3 -m pytest tests/taxonomy

all: install test
