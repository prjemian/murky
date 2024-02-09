def learn_requirements():
    """
    List all installation requirements.

    ALL packages & version restrictions stated in requirements.txt
    """
    req_file = "requirements.txt"
    reqs = []

    import pathlib

    path = pathlib.Path(__file__).parent
    req_file = path.parent / req_file
    if not req_file.exists():
        # not needed with installed package
        return reqs

    excludes = "versioneer coveralls coverage".split()
    with open(req_file, "r") as fp:
        buf = fp.read().strip().splitlines()
        # fmt: off
        for req in buf:
            req = req.strip()
            if (
                req != ""
                and not req.startswith("#")
                and req not in excludes
            ):
                reqs.append(req)
        # fmt: on
    return reqs


# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2014-2022, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------
