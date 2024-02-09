#!/usr/bin/env python

from setuptools import find_packages
from setuptools import setup
import pathlib
import sys
import versioneer

# pull in some definitions from the package's __init__.py file
sys.path.insert(0, (pathlib.Path(__file__).parent / "murky"))
import murky as package

__entry_points__ = {
    "console_scripts": [
        "create_release_notes = murky.create_release_notes:main",
        "murky_tool = murky.murky_tool:main",
    ],
    # 'gui_scripts': [],
}
__scripts__ = [
    "murky/murky_create.sh",
]

# verbose = 1

setup(
    name=package.__package_name__,  # murky
    author_email=package.__author_email__,
    author=package.__author__,
    classifiers=package.__classifiers__,
    description=package.__description__,
    entry_points=__entry_points__,
    include_package_data=True,
    license=package.__license__,
    long_description=package.__long_description__,
    packages=find_packages(exclude=package.__exclude_project_dirs__),
    python_requires=package.__python_version_required__,
    scripts=__scripts__,
    url=package.__url__,
    zip_safe=package.__zip_safe__,
    cmdclass=versioneer.get_cmdclass(),
    version=versioneer.get_version(),
)

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2014-2022, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------
