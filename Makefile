#!/bin/bash

README_HTML=README.html
PYDOCS_DIR=pydocs

default: docs

docs: README.html epydocs
	rst2html.py README.rst $(README_HTML)

README.html: README.rst

epydocs:
	epydoc -q -o $(PYDOCS_DIR) --graph all --parse-only *.py

clean:
	-rm -f *.pyc chromedriver.log ghostdriver.log $(README_HTML)
	-rm -Rf $(PYDOCS_DIR)
