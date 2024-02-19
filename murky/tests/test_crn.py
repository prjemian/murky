"""Test the create_release_notes module."""

import os
import pathlib
import tempfile

import pytest

from .. import create_release_notes as crn


@pytest.fixture(scope="function")
def tmp_path():
    temporary_directory = tempfile.mkdtemp()
    yield pathlib.Path(temporary_directory)


def make_config_file(root_path, org="ORGANIZATION", repo="REPO"):
    git_path = root_path / ".git"
    assert not git_path.exists()
    git_path.mkdir()
    assert git_path.exists()

    config_path = git_path / "config"
    assert not config_path.exists()

    # config file not found, FileNotFoundError is raised
    with pytest.raises(FileNotFoundError):
        crn.findGitConfigFile(git_path)

    # make the config file
    # Just the content useful for testing.
    content = (
        '[remote "origin"]\n'
        f'   url = git@github.com:{org}/{repo}.git\n'
        '   fetch = +refs/heads/*:refs/remotes/origin/*\n'
        ""
    )
    with open(config_path, "w") as fp:
        fp.write(content)
    assert config_path.exists()

    return config_path


def test_findGitConfigFile(tmp_path):
    assert tmp_path.exists()

    config_path = make_config_file(tmp_path)
    assert config_path.exists()

    owd = pathlib.Path.cwd()
    os.chdir(str(tmp_path))
    result = crn.findGitConfigFile()  # no path supplied, defaults to cwd
    assert isinstance(result, pathlib.Path)
    assert result == config_path
    os.chdir(owd)

    path = tmp_path / "other"
    path.mkdir()
    assert crn.findGitConfigFile(path) == config_path


def test_getRepositoryInfo(tmp_path):
    org = "organization_or_ghuser"
    repo = "unit_test_repo"
    config_path = make_config_file(tmp_path, org, repo)
    assert config_path.exists()

    info = crn.getRepositoryInfo(config_path)
    assert info == (org, repo)
