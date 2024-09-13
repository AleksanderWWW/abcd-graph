#!/bin/bash

#  This script will build the package, and publish it to PyPI.
#  Note that the script checks if the tag is consistent with the version specified in  pyproject.toml.
#  If they don't match, the script will exit without publishing the package.
#  This is a safety measure to prevent accidental releases.


CURRENT_VERSION=$(poetry version | awk '{print $2}')
TAG="${GITHUB_REF#refs/tags/}"

# Make sure that we're releasing the version specified in pyproject.toml to PyPI
if [ "$TAG" != "$CURRENT_VERSION" ]; then
    echo "Tag $TAG is inconsistent with current version $CURRENT_VERSION and will not be published on PyPI."
    exit 0
fi

echo "Tag is consistent with the current version. Proceeding with the release."

poetry build

# Publish to PyPI
poetry publish  --username __token__ --password "$1"

echo "Published $CURRENT_VERSION to PyPI."
