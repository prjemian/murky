#!/usr/bin/env python

"""
Update the copyright date in all repository text files.

This is the bash command to find all matching lines::

  grep -iR copyright | grep -i "(c)" | grep -i RIGHT_SIDE_TEXT_MATCH

See copyright text at bottom of this file for example.
"""

# TODO: re-examine from top to bottom
# TODO: consider using a regexp match instead (non-regexp seems easier)

import pathlib
import sys
import mimetypes
import datetime

YEAR = datetime.datetime.now().year
LEFT_SIDE_TEXT_MATCH = "Copyright (C) "  # FIXME: generalize
RIGHT_SIDE_TEXT_MATCH = " Pete R. Jemian"  # FIXME: generalize
ROOT_DIR_EXPECTED_RESOURCES = {
    'files': [".README.md", "setup.py"],
    'subdirs': [".git"],
}
ACCEPTABLE_MIME_TYPES = """
    application/xml
    application/x-msdos-program
    application/xslt+xml
""".strip().split()
IGNORE_EXTENSIONS = """
    .dia .vsdx .h5 .nx .hdf5 .hdf .nx5 .pyc
""".strip().split()


def update(filename):
    """update the copyright year in the file"""

    def position(line, key):
        pos = line.find(key)
        if pos >= 0:
            if line.find("NIAC") >= 0:
                return pos
        return None

    if not pathlib.Path(filename).exists():
        return
    changes = []
    buf = open(filename).readlines()
    for number, line in enumerate(buf):
        pos = position(line, LEFT_SIDE_TEXT_MATCH)
        if pos is None:
            continue  # no match

        pos += len(LEFT_SIDE_TEXT_MATCH)
        text_l = line[:pos]

        text = line[pos:]
        pos = text.find(RIGHT_SIDE_TEXT_MATCH)
        text_r = text[pos:]

        try:
            years = list(map(int, text[:pos].split("-")))
            if len(years) in (1, 2):
                if len(years) == 1:
                    years.append(YEAR)
                elif len(years) == 2:
                    years[1] = YEAR
                line_new = text_l + "-".join(map(str, years)) + text_r
                changes.append(list((number, line_new)))
        except Exception as _exc:
            print(number, filename, str(_exc))

    for number, line in changes:
        buf[number] = line

    if len(changes) > 0:
        print("Update: ", filename)
        with open(filename, "w") as fp:
            fp.writelines(buf)


def find_source_files(path):
    """walk the source_path directories accumulating files to be checked"""
    path = pathlib.Path(path)
    file_list = []
    # TODO: refactor with pathlib & iterdir
    import os
    for root, dirs, files in os.walk(path):
        if root.find("/.git") < 0 or root.find("/kits") < 0:
            file_list = file_list + [os.path.join(root, _) for _ in files]
    return file_list


def sift_file_list(file_list):
    """remove known non-text files and paths"""
    import os  # TODO: refactor with pathlib
    new_list = []
    acceptable_mime_types = ACCEPTABLE_MIME_TYPES
    ignore_extensions = IGNORE_EXTENSIONS
    for fn in file_list:
        _fn = os.path.split(fn)[-1]  # TODO: refactor with pathlib
        mime = mimetypes.guess_type(fn)[0]
        if fn.find("/.git") >= 0:
            continue
        if fn.find("/.settings") >= 0:
            continue
        if fn.find("/kits") >= 0:
            continue
        if fn.find("/build") >= 0:
            continue
        if os.path.splitext(fn)[-1] in ignore_extensions:  # TODO: refactor with pathlib
            continue
        if mime is None or mime.startswith("text/") or mime in acceptable_mime_types:
            new_list.append(fn)
    return new_list


def is_definitions_directory(basedir):
    """Test if ``basedir`` is a repository root."""
    # look for the expected files and subdirectories in the root directory
    basedir = pathlib.Path(basedir)
    for item_list in ROOT_DIR_EXPECTED_RESOURCES.values():
        for item in item_list:
            if not (basedir / item).exists():
                return False
    return True


def qualify_inputs(root_dir):
    """Raise error if this program cannot continue, based on the inputs."""
    root_dir = pathlib.Path(root_dir)
    if not root_dir.exists():
        raise RuntimeError("Cannot find " + root_dir)

    if not root_dir.is_dir():
        raise RuntimeError("Not a directory: " + root_dir)

    if not is_definitions_directory(root_dir):
        msg = "Not a repository root directory " + root_dir
        raise RuntimeError(msg)


def command_args():
    """Get the command-line arguments, handle syntax errors."""
    import argparse

    doc = __doc__.strip().splitlines()[0]
    parser = argparse.ArgumentParser(prog=sys.argv[0], description=doc)
    parser.add_argument(
        "root_dir", action="store", help="repository root directory"
    )
    # TODO: option for LEFT_SIDE_TEXT_MATCH
    # TODO: option for RIGHT_SIDE_TEXT_MATCH
    # TODO: option for ROOT_DIR_EXPECTED_RESOURCES
    return parser.parse_args()


def main():
    """
    Standard command-line processing.
    
    * source directory (repository root dir) named as command line argument
    * target directory is specified (or defaults to present working directory)
    """
    cli = command_args()
    root_dir = pathlib.Path(cli.root_dir).absolute()
    qualify_inputs(root_dir)

    for fn in sift_file_list(find_source_files(root_dir)):
        update(fn)


def __developer_build_setup__():
    """for use with source-code debugger ONLY"""
    import shutil

    # sys.argv.append('-h')
    sys.argv.append("..")


if __name__ == "__main__":
    # __developer_build_setup__()
    main()


# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2014-2022, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

# Adapted from code written by this author for NeXus - Neutron and X-ray Common Data Format
