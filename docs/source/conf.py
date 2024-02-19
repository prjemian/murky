# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import json
import pathlib
import sys
import tomllib

sys.path.append(
    str(pathlib.Path(__file__).parent.parent.parent)
)
import murky  # noqa

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
release = murky.__version__
# release = version.split("+")[0]
version = ".".join(release.split(".")[:2])  # noqa
version_match = f"v{release}"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = """
    sphinx_copybutton
    sphinx.ext.autodoc
    sphinx.ext.autosummary
""".split()

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
# https://pydata-sphinx-theme.readthedocs.io/en/latest/user_guide/version-dropdown.html
#
# html_theme = "alabaster"
html_baseurl = ""
html_static_path = ["_static"]
html_theme = "pydata_sphinx_theme"

# fmt: off
switcher_file = "_static/switcher.json"
switcher_json_url = (
    "https://raw.githubusercontent.com/"
    f"{gh_org}/{project}/"
    "main/docs/source"
    f"/{switcher_file}"
)
with open(switcher_file) as fp:
    switcher_version_list = [
        v["version"]  # to match with ``release`` (above)
        for v in json.load(fp)
    ]
# fmt: on
html_theme_options = {
    "navbar_start": ["navbar-logo", "version-switcher"],
    "switcher": {
        "json_url": switcher_json_url,
        "version_match": release if release in switcher_version_list else "dev"
    },
    "navigation_with_keys": True,
}
