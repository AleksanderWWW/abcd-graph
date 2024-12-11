#!/bin/bash

#  This script will build the package, and publish it to PyPI.
#  It will also build and push docker images to GitHub Container Registry.

set -euo pipefail

if [ -z "$PYPI_TOKEN" ]
  then
    echo "PyPI token not provided. Exiting."
    exit 1
fi

if [ -z "$GHCR_TOKEN" ]
  then
    echo "GHCR token not provided. Exiting."
    exit 1
fi

TAG="${GITHUB_REF#refs/tags/}"

echo "Publishing abcd-graph ${TAG}."

poetry build

# Publish to PyPI
poetry publish  --username __token__ --password "$PYPI_TOKEN"

echo "Published $TAG to PyPI."

echo "Running docker build-and-push"

echo "Logging in to GitHub Container Registry"
docker login --username AleksanderWWW --password "$GHCR_TOKEN" ghcr.io

echo "Building basic docker image"
docker build -t ghcr.io/aleksanderwww/abcd-graph:"$TAG" .

echo "Pushing basic docker image"
docker push ghcr.io/aleksanderwww/abcd-graph:"$TAG"

echo "Building full docker image"
docker build -t ghcr.io/aleksanderwww/abcd-graph-all:"$TAG" --build-arg INSTALL_TYPE=all .

echo "Pushing full docker image"
docker push ghcr.io/aleksanderwww/abcd-graph-all:"$TAG"
