#!/usr/bin/env python

"""
Update the copyright date in all project text files.

Finds text files in ``ROOT_DIR`` and all its subdirectories. In each file, looks
for lines that contain the pattern of ``SYMBOL YEARS OWNER`` (case-independent)
and updates ``YEARS`` to include the current year. YEARS is a list or range of
4-digit numbers.

.. Any content after this line will not appear in the command-line help.

Command Line Application

.. autosummary::

    ~main
    ~command_args

Public API

.. autosummary::
    ~find_source_files
    ~update

Internal Functions

.. autosummary::
    ~revise_copyright_line
    ~is_recognized_text_file
    ~sift_file_list
    ~qualify_inputs
    ~setup_logging

"""
# See copyright text at bottom of this file for another example.

import datetime
import logging
import pathlib
import re
import sys

import magic

YEAR = str(datetime.datetime.now().year)
COPYRIGHT_SYMBOL = "(C)"

_p = pathlib.Path(__file__).parent.parts[-1]
IGNORE_DIRECTORIES = f"""
    {_p}/.git
    {_p}/build
    {_p}/dist
    {_p}/docs/build
    {_p}/.ruff_cache
    {_p}/.vscode
""".strip().split()

ACCEPTABLE_MIME_TYPES = """
    application/json
    application/x-msdos-program
    application/x-yaml
    application/xml
    application/xslt+xml
""".strip().split()

logger = None  # created later, after verbosity is determined


def revise_copyright_line(line, symbol, owner, filename, number):
    """Update the copyright year on one line of filename."""
    # find the part of the text with the date
    p1 = line.lower().find(symbol.lower()) + len(symbol)
    p2 = line.lower().find(owner.lower(), p1)

    # find the 4-digit year or years in the fragment
    fragment = line[p1:p2]
    years = re.findall(r"\d\d\d\d", fragment)
    if len(years) == 0:
        raise ValueError(f"({filename}, {number}) No copyright year(s) in {line!r}")
    # offset of the first year
    p3 = p1 + fragment.find(years[0])
    # offset after the last year
    p4 = p1 + fragment.find(years[-1]) + len(years[-1])

    # build the new list or range of years
    # TODO: YEAR could be a command-line option
    if len(years) == 1:
        if YEAR != years[-1]:
            years = f"{years[0]}-{YEAR}"
            # TODO:
            # if inclusive:
            #     years = f"{years[0]}-{YEAR}"
            # else:
            #     years = ", ".join([years[0], YEAR])
    elif len(years) == 2:
        years = f"{years[0]}-{YEAR}"
    else:
        if YEAR != years[-1]:
            years = ", ".join(years + [YEAR])

    return f"{line[:p3]}{years}{line[p4:]}"


def update(filename, owner, symbol=COPYRIGHT_SYMBOL, dry_run=False):
    """Update the copyright year in filename."""
    global logger

    logger = logger or logging.getLogger(__name__)

    if not filename.exists():
        return

    # fmt: off
    with open(filename) as fp:
        text_file_lines = fp.readlines()
    matching_line_numbers = [
        number
        for number, line in enumerate(text_file_lines)
        if (
            symbol.lower() in line.lower()
            and owner.lower() in line.lower()
        )
    ]
    # fmt: on
    if len(matching_line_numbers) == 0:
        return

    update_available = False
    for number in matching_line_numbers:
        text = text_file_lines[number]
        revision = revise_copyright_line(text, symbol, owner, filename, number)
        if text != revision:
            update_available = True
        logger.debug("(%s,%d):\n---: %r\n+++: %r", filename, number, text, revision)
        text_file_lines[number] = revision

    if not update_available:
        logger.info(f"No changes necessary: {filename}")
        return

    logger.info("Update: %s", filename)
    if dry_run:
        logger.debug("Dry run: original file not changed.")
    else:
        with open(filename, "w") as fp:
            fp.writelines(text_file_lines)


def find_source_files(path):
    """Return a list of all files in path and all of its subdirectories."""
    files = []

    for ignore_dir in IGNORE_DIRECTORIES:
        if str(path).endswith(ignore_dir):
            return []

    for item in path.iterdir():
        if item.is_file():
            files.append(item)
        if item.is_dir() and item.name != ".git":
            files += find_source_files(item)

    return files


def is_recognized_text_file(path):
    """Is the file on this path acceptable as text?"""
    mime = magic.Magic(mime=True).from_file(path)
    # Note: identifies zero-length files as mime="inode/x-empty"

    # fmt: off
    return (
        mime is None
        or mime.startswith("text/")
        or mime in ACCEPTABLE_MIME_TYPES
    )
    # fmt: on


def sift_file_list(file_list):
    """From a list of all files, return a list of the files recognized as text."""
    # fmt: off
    return [
        fn
        for fn in file_list
        if is_recognized_text_file(fn)
    ]
    # fmt: on


def qualify_inputs(root_path):
    """Raise error if this program cannot continue, based on the inputs."""
    if not root_path.exists():
        raise FileExistsError(f"Cannot find {root_path}")

    if not root_path.is_dir():
        raise RuntimeError(f"Not a directory: {root_path}")


def command_args():
    """Get the command-line arguments, handle syntax errors."""
    import argparse

    from . import __version__

    doc = __doc__.strip().splitlines()[0]
    epilog = []
    for line in __doc__.strip().splitlines()[2:]:
        if line.startswith(".. "):
            break
        epilog.append(line)
    epilog = "\n".join(epilog)

    parser = argparse.ArgumentParser(
        prog=sys.argv[0],
        description=doc,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("root_dir", action="store", help="project root directory")
    parser.add_argument("owner", action="store", help="Copyright owner text")
    parser.add_argument(
        "-s",
        "--symbol",
        nargs="?",
        default=COPYRIGHT_SYMBOL,
        action="store",
        help=f"Copyright symbol text.  Default {COPYRIGHT_SYMBOL!r}",
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        default=False,
        action="store_true",
        help="Don't update any files.  Default: False",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        dest="verbosity",
        default=0,
        help="verbose output (repeat for increased verbosity)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_const",
        const=-1,
        default=0,
        dest="verbosity",
        help="quiet output (show errors only), overrides -v option",
    )
    parser.add_argument("-V", "--version", action="version", version=__version__)
    return parser.parse_args()


def setup_logging(verbosity):
    """
    Set up the logging subsystem.

    :see: https://xahteiwi.eu/resources/hints-and-kinks/python-cli-logging-options/
    """
    base_loglevel = 30
    verbosity = min(verbosity, 2)
    loglevel = base_loglevel - (verbosity * 10)
    logging.basicConfig(level=loglevel, format="%(message)s")


def main():
    """
    Entry point for command-line ``update_copyright_date`` application.

    * source directory named as command line argument
    * target directory is specified (or defaults to present working directory)
    """
    global logger

    cli = command_args()
    setup_logging(cli.verbosity)
    logger = logging.getLogger(__name__)

    root_path = pathlib.Path(cli.root_dir).absolute()
    qualify_inputs(root_path)

    file_list = sift_file_list(find_source_files(root_path))
    for fn in file_list:
        update(fn, cli.owner, symbol=cli.symbol, dry_run=cli.dry_run)


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