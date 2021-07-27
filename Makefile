.PHONY: test format

default: test

install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

format:
	black .
	isort .

test:
	pytest

lint:
	flake8 . --config setup.cfg

all: install lint test
