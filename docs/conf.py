# Configuration file for the Sphinx documentation builder.

import os
import sys

# Stops an import error

sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------

project = "abcd-graph"
copyright = "2024 Jordan Barrett & Aleksander Wojnarowicz"
author = "Aleksander Wojnarowicz, Jordan Barrett, and Ryan DeWolfe"
version = "0.5"
release = "0.5.0-beta"
language = "en"

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx_math_dollar",
    "numpydoc",
    "nbsphinx",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

pygments_style = "sphinx"

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# Autodoc settings
autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
    # "special-members": "__init__",
}
autodoc_preserve_defaults = True
# Keep short signatures in docstrings
autodoc_type_aliases = {
    "ArrayLike": "numpy.typing.ArrayLike",
    "Generator": "numpy.random.Generator",
}
# Keeps the string representation intact for alias replacement
autodoc_typehints = "description"

# Suppress return types
napoleon_use_rtype = False

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable", None),
    "scipy": ("https://docs.scipy.org/doc/scipy", None),
    "igraph": ("https://python.igraph.org/en/stable", None),
    "networkx": ("https://networkx.org/documentation/stable", None),
}

# Numpydoc settings
# See https://stackoverflow.com/questions/12206334/sphinx-autosummary-toctree-contains-reference-to-nonexisting-document-warnings/77588774#77588774
numpydoc_show_class_members = False
