.PHONY: all install format lint test

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
	pytest

all: install test
