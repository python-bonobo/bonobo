# This file has been auto-generated.
# All changes will be lost, see Projectfile.
#
# Updated at 2017-05-01 08:35:15.162008

PYTHON ?= $(shell which python)
PYTHON_BASENAME ?= $(shell basename $(PYTHON))
PYTHON_REQUIREMENTS_FILE ?= requirements.txt
PYTHON_REQUIREMENTS_DEV_FILE ?= requirements-dev.txt
QUICK ?= 
VIRTUAL_ENV ?= .virtualenv-$(PYTHON_BASENAME)
PIP ?= $(VIRTUAL_ENV)/bin/pip
PIP_INSTALL_OPTIONS ?= 
PYTEST ?= $(VIRTUAL_ENV)/bin/pytest
PYTEST_OPTIONS ?= --capture=no --cov=bonobo --cov-report html
SPHINX_OPTS ?= 
SPHINX_BUILD ?= $(VIRTUAL_ENV)/bin/sphinx-build
SPHINX_SOURCEDIR ?= docs
SPHINX_BUILDDIR ?= $(SPHINX_SOURCEDIR)/_build
YAPF ?= $(VIRTUAL_ENV)/bin/yapf
YAPF_OPTIONS ?= -rip

.PHONY: $(SPHINX_SOURCEDIR) clean format install install-dev lint test

# Installs the local project dependencies.
install: $(VIRTUAL_ENV)
	if [ -z "$(QUICK)" ]; then \
	    $(PIP) install -U pip wheel $(PIP_INSTALL_OPTIONS) -r $(PYTHON_REQUIREMENTS_FILE) ; \
	fi

# Installs the local project dependencies, including development-only libraries.
install-dev: $(VIRTUAL_ENV)
	if [ -z "$(QUICK)" ]; then \
	    $(PIP) install -U pip wheel $(PIP_INSTALL_OPTIONS) -r $(PYTHON_REQUIREMENTS_DEV_FILE) ; \
	fi

# Cleans up the local mess.
clean:
	rm -rf build
	rm -rf dist

# Setup the local virtualenv, or use the one provided by the current environment.
$(VIRTUAL_ENV):
	virtualenv -p $(PYTHON) $(VIRTUAL_ENV)
	$(PIP) install -U pip wheel
	ln -fs $(VIRTUAL_ENV)/bin/activate activate-$(PYTHON_BASENAME)

lint: install-dev
	$(VIRTUAL_ENV)/bin/pylint --py3k bonobo -f html > pylint.html

test: install-dev
	$(PYTEST) $(PYTEST_OPTIONS) tests

$(SPHINX_SOURCEDIR): install-dev
	$(SPHINX_BUILD) -b html -D latex_paper_size=a4 $(SPHINX_OPTS) $(SPHINX_SOURCEDIR) $(SPHINX_BUILDDIR)/html

format: install-dev
	$(YAPF) $(YAPF_OPTIONS) .
