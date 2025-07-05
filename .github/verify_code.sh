#!/usr/bin/env bash

set -e # enable exit on error

echo -e "\nBuilding Docker image for AmbiHue code..."
docker build -t ambihue_test .

echo -e "\nBuilding Docker image for AmbiHue linters..."
docker build -t test --target=linters .

echo -e "\nRunning Super-Linter in Docker...$(pwd)"
docker run --rm \
	-e DEFAULT_BRANCH=main \
	-e TERM=xterm \
	-e FORCE_COLOR=1 \
	-e LOG_LEVEL=INFO \
	-e RUN_LOCAL=true \
	-e VALIDATE_ALL_CODEBASE=true \
	-e VALIDATE_CHECKOV=false \
	-e VALIDATE_MARKDOWN_PRETTIER=false \
	-e VALIDATE_PYTHON_PYINK=false \
	-v "$(pwd):/tmp/lint" \
	ghcr.io/super-linter/super-linter:slim-v7

# Comments:
# TERM, FORCE_COLOR - Force color output in log
# LOG_LEVEL - Set log level to DEBUG for more verbosity
