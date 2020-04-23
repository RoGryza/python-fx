#!/bin/bash

set -e

poetry run pylint fx
poetry run mypy fx
poetry run isort --check-only --diff fx/*.py
