__project__ = "murky"
__description__ = "The murky package provides tools for working with conda packages."
__copyright__ = "2014-2022, Pete R. Jemian"
__authors__ = [
    "Pete Jemian",
]
__author__ = ", ".join(__authors__)
# __institution__ = u""
__author_email__ = "prjemian@gmail.com"
__url__ = "https://github.com/prjemian/murky/"
__license__ = "(c) " + __copyright__
__license__ += " (see LICENSE file for details)"
__platforms__ = "any"
__zip_safe__ = False
__exclude_project_dirs__ = "docs resources".split()
__python_version_required__ = ">=3.8, <3.12"

__package_name__ = __project__
__long_description__ = __description__

from ._requirements import (
    learn_requirements,
)

__install_requires__ = learn_requirements()
del learn_requirements

__classifiers__ = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Intended Audience :: Science/Research",
    "License :: Freely Distributable",
    "License :: Public Domain",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Software Development",
    "Topic :: Utilities",
]

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2014-2022, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------
