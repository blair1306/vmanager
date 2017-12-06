all:
	@echo "test: testing for python2\ntest2: the same as test\ntest3: testing for python3\n"

test:
	test2

test2:
	cd vmsheder/test && python2 -m pytest

test3:
	cd vmsheder/test && python3 -m pytestk
