#!/bin/bash

README_HTML=README.html
PYDOCS_DIR=pydocs

PYFILES=$(shell git ls-files '*.py')

default: docs

docs: README.html epydocs

README.html: README.rst
	rst2html.py README.rst $(README_HTML)

epydocs:
	epydoc -v -o $(PYDOCS_DIR) --graph all --parse-only $(PYFILES)

check:
	pep8 --max-line-length=120 $(PYFILES)

clean:
	-rm -f *.pyc */*.pyc */*/*.pyc chromedriver.log ghostdriver.log $(README_HTML)
	-rm -Rf $(PYDOCS_DIR)


clean_all: clean

test_self:
	nosetests --with-xunit --xunit-file=nosetests1.xml -v */test
	nosetests run_STAGING.py -v -a SelfTest --with-xunit --xunit-file=nosetests2.xml

precommit:
	nosetests run_user.py -v -a ProdSafe,PreCommit --processes=8 --process-timeout=600
