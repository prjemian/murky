# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import pathlib
import sys
import tomllib

sys.path.append(
    str(pathlib.Path(__file__).parent.parent.parent)
)
import murky as pkg  # noqa

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

root_path = pathlib.Path(__file__).parent.parent.parent
with open(root_path / "pyproject.toml", "rb") as fp:
    toml = tomllib.load(fp)
metadata = toml["project"]

gh_org = toml["tool"]["packaging"]["github_org"]
project = metadata["name"]
copyright = toml["tool"]["packaging"]["copyright"]
author = metadata["authors"][0]["name"]
description = metadata["description"]
rst_prolog = f".. |author| replace:: {author}"
github_url = f"https://github.com/{gh_org}/{project}"
release = pkg.__version__
# release = version.split("+")[0]
version = ".".join(release.split(".")[:2])  # noqa
version_match = f"v{release}"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = """
sphinx_copybutton
""".split()

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
#
# html_theme = "alabaster"
html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]

html_baseurl = ""
html_theme_options = {
    # https://pydata-sphinx-theme.readthedocs.io/en/latest/user_guide/version-dropdown.html
    "switcher": {
        "json_url": "https://raw.githubusercontent.com/prjemian/murky/main/switcher.json",
        "version_match": version_match,
    },
   "navbar_start": ["navbar-logo", "version-switcher"],
}
