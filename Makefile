.PHONY: test format

default: test

format:
	black .; isort .

test:
	PYTHONPATH=./defects4cpp pytest
