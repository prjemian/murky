.. _create_release_notes:

====================
create_release_notes
====================

Create detailed release notes for a new release of a GitHub repository.

.. code-block:: bash
    :linenos:

    $ create_release_notes -h
    usage: create_release_notes [-h] [--head [HEAD]] base milestone token

    Create detailed release notes for a new release of a GitHub repository. Run from the root directory of a package.

    positional arguments:
    base           name of tag to start the range
    milestone      name of milestone
    token          personal access token (see: https://github.com/settings/tokens)

    options:
    -h, --help     show this help message and exit
    --head [HEAD]  name of tag, branch, SHA to end the range (default="master")

--------

Source Code Documentation
=========================

.. automodule:: murky.create_release_notes
    :members:
