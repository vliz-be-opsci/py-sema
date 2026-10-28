TEST_PATH = ./tests/
FLAKE8_EXCLUDE = venv,.venv,.eggs,.tox,.git,__pycache__,*.pyc
MODULE = sema
AUTHOR = "Flanders Marine Institute, VLIZ vzw"

REPONAME = py-sema

.PHONY: help clean startup install init init-dev init-docs docs docs-build test test-quick test-with-graphdb test-coverage test-coverage test-coverage-with-graphdb check lint-fix update
.DEFAULT_GOAL := help

help:  ## Shows this list of available targets and their effect.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

clean:  ## removes all possible derived built results from other executions of the make
	@find . -name '*.pyc' -exec rm --force {} +
	@find . -name '*.pyo' -exec rm --force {} +
	@find . -name '*~' -exec rm --force {} +
	@rm -rf build
	@rm -rf dist
	@rm -rf *.egg-info
	@rm -f *.sqlite
	@rm -rf .cache

subyt-update: ## prepares environment for using git submodules
	@git submodule update --init --recursive

startup: ## prepares environment for using uv
	@pip install --upgrade pip
	@which uv >/dev/null || pip install uv

install:  ## install this package in the current environment
	@uv sync

init-base: startup subyt-update install  ## initial prepare of the environment for local execution of the package

init: init-dev  ## alias for init-dev

init-dev: startup subyt-update  ## initial prepare of the environment for further development in the package
	@uv sync --all-groups

init-docs: startup subyt-update  ## initial prepare of the environment for local execution and reading the docs
	@uv sync


#docs:  ## builds the docs
#	@poetry run sphinx-quickstart -q --ext-autodoc --ext-githubpages --ext-viewcode --sep --project $(MODULE) --author '${AUTHOR} -f' source_docs
#	@cp ./docs/* ./source_docs/source/
#	@sleep 1
#	@poetry run sphinx-apidoc -o ./source_docs/source ./$(MODULE)
#	@poetry run sphinx-build -b html ./source_docs/source ./source_docs/build/html
#	@cp ./source_docs/source/custom.css ./source_docs/build/html/_static/custom.css

test-single:  ## runs the standard test-suite for the memory-graph implementation
	@for file in $$(find ${TEST_PATH} -name 'test_*.py'); do \
		if grep -q $(filter-out $@,$(MAKECMDGOALS)) $$file; then \
			uv run pytest $$file::$(filter-out $@,$(MAKECMDGOALS)); \
		fi \
	done

%:
	@:

test:              ## runs the tests
	uv run pytest ${TEST_PATH}

test-module: ## runs a given module when testing, module can be the following: bench, common, harvest, query, subyt, syncfs, clean, cli, env, j2, j2-template, log, path, prov, serv, store
	@for folder in $$(find ${TEST_PATH} -type d -name $(filter-out $@,$(MAKECMDGOALS))); do \
		for file in $$(find $$folder -name 'test_*.py'); do \
			uv run pytest $$file; \
		done \
	done

test-quick:  ## runs tests more quickly by skipping some lengthy ones
	@(export QUICKTEST=1 && $(MAKE) test --no-print-directory)

test-with-graphdb: ## runs the standard test-suite for all available implementations (requires docker to spin up a sparql endpoint)
	@(export REPONAME=${REPONAME} && ./tests/kgap-graphdb.sh start-wait)
	-@(export TEST_SPARQL_READ_URI=http://localhost:7200/repositories/${REPONAME} TEST_SPARQL_WRITE_URI=http://localhost:7200/repositories/${REPONAME}/statements && $(MAKE) test --no-print-directory)
	@./tests/kgap-graphdb.sh stop

test-coverage:  ## runs the standard test-suite for the memory-graph implementation and produces a coverage report
	@uv run pytest --cov=$(MODULE) ${TEST_PATH} --cov-report term-missing

test-coverage-with-graphdb:  ## runs the standard test-suite for all available implementations and produces a coverage report
	@(export REPONAME=${REPONAME} && ./tests/kgap-graphdb.sh start-wait)
	-@(export TEST_SPARQL_READ_URI=http://localhost:7200/repositories/${REPONAME} TEST_SPARQL_WRITE_URI=http://localhost:7200/repositories/${REPONAME}/statements && $(MAKE) test-coverage --no-print-directory)
	@./tests/kgap-graphdb.sh stop

check:  ## performs linting on the python code
	@uv run black --check --diff .
	@uv run isort --check --diff .
	@uv run flake8 . --exclude ${FLAKE8_EXCLUDE} --ignore=E203,W503

lint-fix:  ## fixes code according to the lint suggestions
	@uv run black .
	@uv run isort .

update:  ## updates dependencies
	@uv pip compile pyproject.toml --upgrade -o uv.lock 2>/dev/null || uv lock

build: update check test docs  ## builds the package
	@uv build

release: build  ## releases the package
	@uv publish
