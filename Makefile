all: help

help:
	@echo "run: run this program\ntest: run tests for python2\ntest2: the same as test\ntest3: run tests for python3\n"

run:
	cd vmanager/test && python test_main.py

test: test2

test2:
	cd vmanager/test && python2 -m pytest

test3:
	cd vmanager/test && python3 -m pytest