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
    ~find_years_indices
    ~is_recognized_text_file
    ~qualify_inputs
    ~revise_copyright_line
    ~setup_logging
    ~sift_file_list
    ~UnexpectedSeparatorError
    ~YearsNotFound

"""
# See copyright text at bottom of this file for another example.

import datetime
import logging
import pathlib
import re
import sys

import magic

COPYRIGHT_SYMBOL = "(C)"
THIS_YEAR = str(datetime.datetime.now().year)
LAST_YEAR = str(int(THIS_YEAR) - 1)

_p = pathlib.Path(__file__).parent.parts[-1]
IGNORE_DIRECTORIES = f"""
    {_p}/.git
    {_p}/build
    {_p}/dist
    {_p}/docs/build
    {_p}/.pytest_cache
    {_p}/.ruff_cache
    {_p}/.vscode
    /__pycache__
""".strip().split()

ACCEPTABLE_MIME_TYPES = """
    application/json
    application/x-msdos-program
    application/x-yaml
    application/xml
    application/xslt+xml
""".strip().split()

logger = None  # created later, after verbosity is determined


class UnexpectedSeparatorError(ValueError):
    """Separator between years in copyright notice was not expected."""


class YearsNotFound(ValueError):
    """Did not find list or range of years in matching copyright line."""


def find_years_indices(line, symbol, owner):
    """Return the start and end indices of the copyright years in the text."""
    # find the part of the text with the date
    p1 = line.lower().find(symbol.lower()) + len(symbol)
    p2 = line.lower().find(owner.lower(), p1)

    # find the 4-digit year or years in the fragment
    fragment = line[p1:p2]
    years = re.findall(r"\d\d\d\d", fragment)
    if len(years) == 0:
        raise YearsNotFound(f"Copyright year(s) not found: {line!r}")
    # offset of the first year
    p3 = p1 + fragment.find(years[0])
    # offset after the last year
    p4 = p1 + fragment.find(years[-1]) + len(years[-1])
    return years, p3, p4


def revise_copyright_line(line, symbol, owner, year):
    """
    Update the copyright year on this line.

    PARAMETERS

    line : *str*
        Line of text that contains a copyright notice.
    symbol : *str*
        The text to be found *before* the text with the years.
    owner : *str*
        The text to be found *after* the text with the years.
    year : *str*
        Line of text that contains a copyright notice.
    """
    previous_year = str(int(year) - 1)
    years_list, start_index, end_index = find_years_indices(line, symbol, owner)
    # At this point, years is a non-empty list of 4-digit years (str).
    years_str = line[start_index:end_index]

    if year not in years_list:
        if len(years_list) == 1:
            # note: years_str == years_list[0] == years_list[-1]
            if years_str == previous_year:
                years_str = f"{years_str}-{year}"
            else:
                years_str = f"{years_str}, {year}"
        else:  # more than one year
            if years_list[-1] == previous_year:
                # Check if the last year was part of a hyphenated or comma-separated list.
                index_year1 = years_str.find(years_list[-2])
                index_year2 = years_str.find(years_list[-1])
                separator = years_str[index_year1 + len(years_list[-2]) : index_year2]
                if separator.strip() == "-":
                    years_str = (
                        f"{years_str[:index_year1]}{years_list[-2]}{separator}{year}"
                    )
                elif separator.strip() == ",":
                    years_str = f"{years_str}-{year}"
                else:
                    raise UnexpectedSeparatorError(f"Unexpected {separator=!r}")
            else:
                years_str = f"{years_str}, {year}"

    # Splice the years back into the line.
    return f"{line[:start_index]}{years_str}{line[end_index:]}"


def update(
    filename,
    owner,
    symbol=COPYRIGHT_SYMBOL,
    dry_run=False,
    year=THIS_YEAR,
):
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
        logger.debug("No matching copyright notices: %s", filename)
        return

    changes = {}  # key: line number, value: revised text for this line
    for number in matching_line_numbers:
        text = text_file_lines[number]
        try:
            revision = revise_copyright_line(text, symbol, owner, year)
        except (UnexpectedSeparatorError, YearsNotFound) as exinfo:
            logger.error("(%s,%d) %s", filename, number, exinfo)
            continue
        if text != revision:
            changes[number] = revision
        logger.debug("(%s,%d):\n---: %r\n+++: %r", filename, number, text, revision)

    if len(changes) == 0:
        logger.debug("No changes necessary: %s", filename)
        return

    if dry_run:
        logger.debug("Dry run: original file not changed: %s", filename)
        return

    logger.info("Update with %d line(s) changed: %s", len(changes), filename)
    for number, revision in changes.items():
        text_file_lines[number] = revision
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
        help=f"Copyright symbol text.  Default: {COPYRIGHT_SYMBOL!r}",
    )
    parser.add_argument(
        "-y",
        "--year",
        nargs="?",
        default=None,
        action="store",
        help=f"Final copyright year.  Default: {THIS_YEAR!r}",
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
        update(
            fn,
            cli.owner,
            symbol=cli.symbol,
            dry_run=cli.dry_run,
            year=cli.year,
        )


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
