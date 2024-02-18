.. _update_copyright_date:

=====================
update_copyright_date
=====================

Update the copyright date in all (project) text files.

Motivation
==========

A software project under active development and maintenance should edit its
copyright notice annually to include (or extend) to the current year.  This
task is often neglected as a project matures when the number of files to be
updated increases.  Sometimes, the copyright notice in some files is missed.

How does it work?
=================

The code looks through all text files for lines with a copyright notice.
The search is independent of upper or lower case.
Consider these examples::

    # Copyright (C) 1988-2020 Free Software Foundation, Inc.
    Copyright (C) 2008-2022 NeXus International Advisory Committee (NIAC)
    Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>
    # Copyright (c) 2006, 2008 Junio C Hamano
    Copyright (C) 2000, 2001, 2002, 2007, 2008 Free Software Foundation, Inc.
    copyright = "(c) 2014-2024, Project Copyright Owner"
    Copyright 2015 Jane Doe
    Copyright (c) 1215, 1871, 1973, 1975-1991, 2024 Some Project Owner

The code edits the list or range of years to include the current year.
For example, when run in 2024, the *years* in these examples are:

=================================   =============================================
before                              after
=================================   =============================================
``1988-2020``                       ``1988-2024``
``2008-2022``                       ``2008-2024``
``2007``                            ``2007-2024``
``2006, 2008``                      ``2006, 2008, 2024``
``2000, 2001, 2002, 2007, 2008``    ``2000, 2001, 2002, 2007, 2008, 2024``
``2000``                            ``2000-2024``
``2014-2024``                       ``2014-2024`` (same, so file is not changed)
``2015``                            ``2015-2024``
``1215, 1871, 1914-1918, 2008``     ``1215, 1871, 1914-1918, 2008, 2024``
=================================   =============================================

Copyright notices share a common format.  [#]_

  Generally, a copyright notice will read something like "Copyright 2015 Jane Doe."

The list or range of years is identified by matching common text before and
after the text that describes the years.  It is common that the text *before*
the years is the text representation of the copyright symbol (``"(C)"``).  The
text *after* the years is the name of the copyright owner. The years are four
digit numbers.

..  [#] See *How to Make a Copyright Notice*:
    https://www.wikihow.com/Make-a-Copyright-Notice

Example
=======

Consider a file with this copyright notice::

    Copyright (c) 1215, 1871, 1973, 1975-1991 Some Project Owner

In 2024, executing command::

    update_copyright_date.py -s "(c)" . Owner

updates the years in the copyright notice to::

    Copyright (c) 1215, 1871, 1973, 1975-1991, 2024 Some Project Owner

..  note:: This is a comparable bash shell command to *find* (but not replace) all matching lines:

    .. raw:: html

        <embed>
        <pre>
        $ <em>grep -iIR "(c)" | grep -i Owner</em>
        </pre>
        </embed>

Command Positional Arguments
============================

``root_dir``
  Directory with the text files with copyrights to be updated.  A value of ``.``
  means the current directory. The value can be a relative path (such as ``.``
  or ``../project``) or an absolute path (such as
  ``/home/user/Documents/project/``).

``owner``
  The text to be matched that appears *after* the years.  Typically, the name of
  the copyright owner.

Command Options
===============

Command line options may be combined as long as any parameters required by an
option appear in the correct order.

* ``-v`` is the same as ``--verbose``
* ``-vv`` is the same as ``-v -v`` or ``--verbose --verbose``
* ``-dvvs "(C)"`` is the same as ``--dry-run -vv --symbol "(C)"`` (Note that the
  ``s`` option must come last since its required parameter must appear next.)

``-h``, ``--help``
++++++++++++++++++

Help for how to use the command-line program:

.. raw:: html

    <embed>
    <pre>
    $ <em>update_copyright_date <b>--help</b></em>
    usage: update_copyright_date [-h] [-s [SYMBOL]] [-y [YEAR]] [-i] [-d] [-v] [-q] [-V] root_dir owner

    Update the copyright date in all project text files.

    positional arguments:
    root_dir              project root directory
    owner                 Copyright owner text

    options:
    -h, --help            show this help message and exit
    -s [SYMBOL], --symbol [SYMBOL]
                            Copyright symbol text. Default: '(C)'
    -y [YEAR], --year [YEAR]
                            Final copyright year. Default: '2024'
    -d, --dry-run         Don't update any files. Default: False
    -v, --verbose         verbose output (repeat for increased verbosity)
    -q, --quiet           quiet output (show errors only), overrides -v option
    -V, --version         show program's version number and exit

    Finds text files in ``ROOT_DIR`` and all its subdirectories. In each file, looks
    for lines that contain the pattern of ``SYMBOL YEARS OWNER`` (case-independent)
    and updates ``YEARS`` to include the current year. YEARS is a list or range of
    4-digit numbers.
    $
    </pre>
    </embed>

The ``--help`` option overrides any other options.

``-s``, ``--symbol``
++++++++++++++++++++

The text to be matched that appears *before* the years.
The default SYMBOL is ``(C)``, common to many copyright notices.

.. raw:: html

    <embed>
    <pre>
    $ <em>update_copyright_date . Owner</em>
    $
    </pre>
    </embed>

which is equivalent to:

.. raw:: html

    <embed>
    <pre>
    $ <em>update_copyright_date <b>--symbol "(C)"</b> . Owner</em>
    $
    </pre>
    </embed>

Quotes are necessary around the ``(C)`` to indicate to the shell that SYMBOL is
verbatim text and not a shell expansion.

To match ``Copyright 2015 Jane Doe``, use these definitions of SYMBOL and OWNER
in the command line:

.. raw:: html

    <embed>
    <pre>
    $ <em>update_copyright_date <b>--symbol Copyright</b> . <b>"Jane Doe"</b></em>
    $
    </pre>
    </embed>

Quotes are necessary around the text ``Jane Doe`` to indicate to the shell that SYMBOL has
both words.

``-y``, ``--year``
++++++++++++++++++++

The new year to be added. The default is the current year.

.. raw:: html

    <embed>
    <pre>
    $ <em>update_copyright_date -d <b>--year 2125</b> . Jemian</em>
    $
    </pre>
    </embed>

``-d``, ``--dry-run``
+++++++++++++++++++++

A *dry run* shows what changes will be made without modifying any files.

.. raw:: html

    <embed>
    <pre>
    $ <em>update_copyright_date <b>-dry-run</b> . Jemian</em>
    $
    </pre>
    </embed>

``-v``, ``--verbose``
+++++++++++++++++++++

Increase the level of progress messages.  Warnings and errors will always be
reported. Use once to add information messages.  Use twice to add both
information and debugging messages.  More than two will be the same two.

.. raw:: html

    <embed>
    <pre>
    $ <em>update_copyright_date <b>-d</b> <b>-v</b> . Jemian</em>
    No changes necessary: .../murky/pyproject.toml
    No changes necessary: .../murky/murky/murky_tool.py
    No changes necessary: .../murky/murky/update_copyright_date.py
    No changes necessary: .../murky/murky/murky_create.sh
    No changes necessary: .../murky/murky/create_release_notes.py
    $
    </pre>
    </embed>

``-q``, ``--quiet``
+++++++++++++++++++++

Do not write anything to the console, except for warnings and error messages.
This option overrides any ``--verbose`` options.

.. raw:: html

    <embed>
    <pre>
    $ <em>update_copyright_date <b>-d</b> <b>-v</b> . Jemian</em>
    No changes necessary: .../murky/pyproject.toml
    No changes necessary: .../murky/murky/murky_tool.py
    No changes necessary: .../murky/murky/update_copyright_date.py
    No changes necessary: .../murky/murky/murky_create.sh
    No changes necessary: .../murky/murky/create_release_notes.py
    $
    </pre>
    </embed>

``-V``, ``--version``
+++++++++++++++++++++

Software version of this application. The ``--version`` option overrides any
other options except ``--help``.

.. raw:: html

    <embed>
    <pre>
    $ <em>update_copyright_date <b>--version</b></em>
    $
    </pre>
    </embed>

--------

Source Code Documentation
=========================

.. automodule:: murky.update_copyright_date
    :members:
