.PHONY: help install pre-commit build test lint format

.DEFAULT: help
help:
	@echo "make install"
	@echo "       install all the dependencies specified in pyproject.toml and poetry.lock"
	@echo "make update-install"
	@echo "       runs poetry lock without updates and installs all the dependencies specified in pyproject.toml and poetry.lock"
	@echo "make pre-commit"
	@echo "       install the pre-commit and pre-push hooks"
	@echo "make build"
	@echo "       packages the application in wheel format"
	@echo "make azure-func"
	@echo "       Starts the Azure Function"
	@echo "make azure-login"
	@echo "       Logs in in Azure"
	@echo "make test"
	@echo "       run tests and coverage checks"
	@echo "make app"
	@echo "       ensures that the branch is ready to push"
	@echo "make show-coverage"
	@echo "       run coverage checks and open the html report"
	@echo "make cleanup-tests"
	@echo "       run cleanup of test/cache files"
	@echo "make pre-commit-manual"
	@echo "       run isort, black, flake8, mypy, tests and coverage checks"
	@echo "make lint"
	@echo "       run flake8 and mypy"
	@echo "make format"
	@echo "       run isort and black"
	@echo "make terraform-modules"
	@echo "       install all terraform module version dependencies. requires azure login"
	@echo "make terraform-fmt"
	@echo "       finds all terraform files and formats them"
	@echo "make help"
	@echo "       print this help message"

install:
	poetry install

update-install:
	poetry lock --no-update
	poetry install

pre-commit:
	poetry run pre-commit install -t pre-commit
	poetry run pre-commit install -t pre-push

build:
	poetry build

test:
	poetry run pytest -v --cov --no-coverage-upload --cov-branch -p no:cacheprovider
	make coverage
	make cleanup-tests

app:
	make update-install
	make pre-commit-manual

coverage:
	poetry run coverage json
	poetry run coverage-threshold

show-coverage:
	poetry run pytest -v --cov --cov-report=html --no-coverage-upload
	open reports/site/index.html

cache-clear:
	find . -type d -name "*_cache*" -exec rm -rf {} +

cleanup-tests:
	# for reports folders
	find ./tests -type d -name "reports" -exec rm -rf {} +
	rm -rf reports

	# for cache
	make cache-clear

	# for coverage results
	find . \( -name "test-output.xml" -o -name "coverage.xml" -o -name "coverage.json" -o -name ".coverage" \) -delete

site:
	poetry run pytest -v --cov --cov-report=html --no-coverage-upload

lint:
	mkdir -p reports
	poetry run flake8
	poetry run mypy

format:
	poetry run isort .
	poetry run black .

ci-lint-flake8:
	mkdir -p reports
	poetry run flake8 --format junit-xml --output-file reports/lint-flake8.xml

ci-lint-mypy:
	poetry run mypy --junit-xml reports/lint-mypy.xml

ci-test:
	poetry run pytest -v --cov --cov-report=xml --no-coverage-upload --cov-branch
	make coverage

pre-commit-manual:
	poetry run isort .
	poetry run black .
	poetry run flake8
	poetry run mypy
	make test
