# Contributing

Contributions of all kinds are welcome. In particular pull requests are appreciated.
The authors will endeavour to help walk you through any issues in the pull request
discussion, so please feel free to open a pull request even if you are new to such things.

## Issues

The easiest contribution to make is to [file an issue](https://github.com/AleksanderWWW/abcd-graph/issues/new). Please do a cursory search of [existing issues](https://github.com/AleksanderWWW/abcd-graph/issues?utf8=%E2%9C%93&q=is%3Aissue) since there could be other's
in a similar situation. It is also helpful, but not necessary, if you can provide clear
instruction for  how to reproduce a problem.

## Documentation

Contributing to documentation is the easiest way to get started. Providing simple
clear or helpful documentation for new users is critical. Anything that *you* as
a new user found hard to understand, or difficult to work out, are excellent places
to begin. Contributions to more detailed and descriptive error messages is
especially appreciated. To contribute to the documentation please
[fork the project](https://github.com/AleksanderWWW/abcd-graph/fork)
into your own repository, make changes there, and then submit a pull request.

### Building the Documentation Locally

First, clone the project or your fork and nagivate to the repository.
To install the required packages, run

```bash
pip install ".[dev,docs]"
```

or if you are using uv

```bash
uv sync --group docs
```

To build the documentation, run

```bash
sphinx-build docs docs/_build
```

or again if using uv

```bash
uv run sphinx-build docs docs/_build
```

If you get an error talking about `pandoc`, it's likely that you do not have pandoc
installed. The pypi pandoc library is only a wrapper around the actual pandoc library,
which is not python so must be installed separately. See
[installing pandoc](https://pandoc.org/installing.html) for more details.

The built documentation is in `docs/_build` in HTML format. Start by opening `index.html`.

## Code

Code contributions are always welcome, from simple bug fixes, to new features. To
contribute code please
[fork the project](https://github.com/TutteInstitute/AleksanderWWW/abcd-graph/fork)
into your own repository, make changes there, and then submit a pull request. If
you are fixing a known issue please add the issue number to the PR message. If you
are fixing a new issue feel free to file an issue and then reference it in the PR.

### Pull request size

Small pull requests are reviewed and merged faster. Prefer PRs that add or extend
functionality while leaving every existing test unchanged, and keep any PR that
modifies or removes existing tests separate and focused on that change, so reviewers
can see exactly which behaviour changed. For anything larger than a small fix, please
open an issue or draft PR first so we can agree on the scope.

### Running the Tests

Our testing framework uses `pytest`, and all tests live in the top level `/test` folder.
Please make sure any changes come with updates unit tests.

```bash
pip install . --group dev
pytest tests
```

or using uv

```bash
uv sync
uv run pytest tests
```

There is also a speed test in `benchmarks/test_benchmark.py`, which you should run if your
changes are meant to improve speed or cause a significant performance regression. Running
the benchmark will take a few mintues.

To make fair local comparisons, before making your changes run

```bash
pytest --benchmark-only \
       --benchmark-json=baseline.json \
       --benchmark-warmup=on \
       --benchmark-warmup-iterations=10 \
       --benchmark-min-rounds=10
```

(with `uv run` if using uv). This will save the benchmar results to a file called `baseline.json`, which you can compare to after making your changes. **Do not** commit
this file to git.

After making your changes, run (with uv if necessary)
```bash
pytest --benchmark-only \
       --benchmark-compare=baseline.json \
       --benchmark-compare-fail=median:10% \
       --benchmark-warmup=on \
       --benchmark-warmup-iterations=10 \
       --benchmark-min-rounds=10 \
```

The test will fail if the median sample speed increases by more than 10%. A similar test
runs in CI, but with a more generous failure margin due to inconsistency in the github
action servers.

### Code formatting

This project uses `ruff` for code formatting and `ty` for type checking. The CI system
will automatically check that code changes pass both requirements by running a pre-commit
hook. You can run the pre-commit locally using `prek` (which is installed as part of the
dev packages).

```bash
pip install . --group dev
prek run --all-files
```

or using uv

```bash
uv sync
uv run prek
```

If the check fails, you'll see which files need formatting.
