#!/usr/bin/env python

"""
Tool used in support of murky_create.sh

.. autosummary::

    ~main
    ~print_pip_requirements
    ~print_conda_requirements
    ~print_environment_name
    ~get_user_parameters
"""

import argparse
import yaml


def print_pip_requirements(specs):
    """Command function: print **pip** requirements."""
    for req in specs["dependencies"]:
        # print(req)
        if isinstance(req, dict):
            reqs = req.get("pip")
            if reqs is not None:
                print("\n".join(sorted(reqs)))


def print_conda_requirements(specs):
    """Command function: print **conda** requirements."""
    dependencies = []
    if "dependencies" in specs:  # if NOT, then why bother with this?
        for req in specs["dependencies"]:
            if isinstance(req, dict):
                if req.get("pip") is None:
                    dependencies.append(req)
            else:
                dependencies.append(req)
        specs["dependencies"] = dependencies
    print(yaml.dump(specs))


def print_environment_name(specs):
    """Command function: print environment **name**."""
    print(specs["name"])


def get_user_parameters():
    """Command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="hybrid_tool",
    )
    parser.add_argument("function", action="store", help="one of: name, pip, conda")
    parser.add_argument("env_file", action="store", help="environment YAML file")
    return parser.parse_args()


def main():
    """Command-line application program."""
    args = get_user_parameters()
    func = dict(
        conda=print_conda_requirements,
        name=print_environment_name,
        pip=print_pip_requirements,
    )[args.function]

    with open(args.env_file, "r") as f:
        all_specs = yaml.safe_load(f)

    func(all_specs)


if __name__ == "__main__":
    main()

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2014-2024, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------
