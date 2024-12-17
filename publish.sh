#!/bin/bash

#  This script will build the package, and publish it to PyPI.
# It will also build and push docker images to GitHub Container Registry.
#  Note that the script checks if the tag is consistent with the version specified in  pyproject.toml.
#  If they don't match, the script will exit without publishing the package.
#  This is a safety measure to prevent accidental releases.
set -euo pipefail

CURRENT_VERSION=$(cat pyproject.toml | awk -F '"' '/^version =/ { print $2; exit }')
TAG="${GITHUB_REF#refs/tags/}"

# Make sure that we're releasing the version specified in pyproject.toml to PyPI
if [ "$TAG" != "$CURRENT_VERSION" ]; then
    echo "Tag $TAG is inconsistent with current version $CURRENT_VERSION and will not be published on PyPI."
    exit 1
fi

echo "Tag is consistent with the current version. Proceeding with the release."

uv build

# Publish to PyPI
uv publish --token "$1"

echo "Published $CURRENT_VERSION to PyPI."

echo "Running docker build-and-push"

echo "Logging in to GitHub Container Registry"
docker login --username AleksanderWWW --password "$2" ghcr.io

echo "Building basic docker image"
docker build -t ghcr.io/aleksanderwww/abcd-graph:"$TAG" .

echo "Pushing basic docker image"
docker push ghcr.io/aleksanderwww/abcd-graph:"$TAG"

echo "Building full docker image"
docker build -t ghcr.io/aleksanderwww/abcd-graph-all:"$TAG" --build-arg INSTALL_TYPE=all .

echo "Pushing full docker image"
docker push ghcr.io/aleksanderwww/abcd-graph-all:"$TAG"
