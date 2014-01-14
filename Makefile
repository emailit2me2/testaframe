#!/bin/bash

README_HTML=README.html

default: docs

docs: README.html
	rst2html.py README.rst $(README_HTML)

README.html: README.rst

clean:
	rm -f *.pyc chromedriver.log ghostdriver.log $(README_HTML)
