#!/bin/bash

#  This script will build the package, and publish it to PyPI.

set -euo pipefail

if [ -z "$PYPI_TOKEN" ]
  then
    echo "PyPI token not provided. Exiting."
    exit 1
fi

TAG="${GITHUB_REF#refs/tags/}"

echo "Publishing abcd-graph ${TAG}."

poetry build

# Publish to PyPI
poetry publish  --username __token__ --password "$PYPI_TOKEN"

echo "Published $TAG to PyPI."
