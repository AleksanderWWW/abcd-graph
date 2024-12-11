# Releasing a new version of the project

This document describes the procedure for releasing a new version of the project.
Following the steps below for a release `X.Y.Z` should result in creating:
- a new tag on GitHub with the version `X.Y.Z`
- a new release on GitHub named `X.Y.Z`
- a new version on PyPI with the version `X.Y.Z`.
- new docker image tags with the version `X.Y.Z`.

## Steps

The steps assume that you know the version number for the release.
A placeholder `X.Y.Z` is used to represent the version number.
The same procedure applies for release candidates - just replace `X.Y.Z` with `X.Y.ZrcN`.

### Prepare the release
- Switch to the main branch and pull all the changes.

```bash
git checkout main
git pull --rebase
git fetch --all
```

- Create a new branch for the release.

```bash
git checkout -b release/abcd-X.Y.Z
```

- [Not applicable for release candidates!!!] Update the changelog - remove the [UNRELEASED] part of the top-most part of the file.

before:
```markdown
## [UNRELEASED] abcd-graph X.Y.Z
```

after:
```markdown
## abcd-graph X.Y.Z
```

- Commit the changes.

```bash
git add CHANGELOG.md
git commit -m "Release abcd-graph X.Y.Z"
git push -u origin release/abcd-X.Y.Z
```

- Make a GitHub pull request for the release branch.
Once this PR is merged, the release can be made.

- Create a new release on GitHub.
  - Go to the [releases page](https://github.com/AleksanderWWW/abcd-graph/releases/new)
  - Fill in the tag version `X.Y.Z` (choose the option to create a new tag)
  - Fill in the release title `X.Y.Z`
  - Fill in the release description with the changes since the last release (copy from changelog).
  - Publish the release (set as pre-release in case of release candidates).
- Wait for the CI to finish and the release to be built.
- Once the release is built, check that the package is available on PyPI and new image tags are present on GHCR.
