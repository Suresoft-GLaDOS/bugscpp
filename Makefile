.PHONY: test format

default: test

format:
	black .; isort .

test:
	pytest
