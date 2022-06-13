import importlib.metadata

# -- General configuration ------------------------------------------------------------

extensions = [
    # first-party extensions
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.todo",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    # third-party extensions
    "myst_parser",
]

# -- Project information -----------------------------------------------------

project = "pkg_metadata"
copyright = "2022, Paul Moore"
author = "Paul Moore"
release = importlib.metadata.version(project)

# -- Options for myst-parser ----------------------------------------------------------

myst_enable_extensions = ["deflist"]
myst_heading_anchors = 3

# -- Options for smartquotes ----------------------------------------------------------

# Disable the conversion of dashes so that long options like "--find-links" won't
# render as "-find-links" if included in the text.The default of "qDe" converts normal
# quote characters ('"' and "'"), en and em dashes ("--" and "---"), and ellipses "..."
smartquotes_action = "qe"

# -- Options for intersphinx ----------------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pypug": ("https://packaging.python.org", None),
}

# -- Options for extlinks -------------------------------------------------------------

extlinks = {
    "issue": ("https://github.com/pypa/pip/issues/%s", "#%s"),
    "pull": ("https://github.com/pypa/pip/pull/%s", "PR #%s"),
    "pypi": ("https://pypi.org/project/%s/", "%s"),
}


# -- Options for HTML -----------------------------------------------------------------

html_theme = "furo"
html_title = f"{project} {release}"

# Disable the generation of the various indexes
# html_use_modindex = False
# html_use_index = False
