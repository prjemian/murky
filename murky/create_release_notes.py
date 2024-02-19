#!/usr/bin/env python

"""
Create detailed release notes for a new release of a GitHub repository.

Run from the root directory of a package.

.. autosummary::

    ~main
    ~findGitConfigFile
    ~_parse_git_url
    ~getRepositoryInfo
    ~get_release_info
    ~parse_command_line
    ~report
"""

# Requires:
#
# * assumes current directory is within a repository clone
# * pyGithub (conda or pip install) - https://pygithub.readthedocs.io/
# * Github personal access token (https://github.com/settings/tokens)
#
# Github token access is needed or the GitHub API limit
# will likely interfere with making a complete report
# of the release.

import argparse
import configparser
import datetime
import logging
import pathlib
import urllib

import github

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("create_release_notes")


def findGitConfigFile(path=None):
    """
    Return full path to ``ROOT/.git/config`` file.

    Supplied 'path' must be in the ROOT directory or a subdirectory.

    This is a simplistic search that could be improved by using
    an open source package.
    """
    path = pathlib.Path(path or pathlib.Path.cwd())
    original_path = path
    while path != path.parent:
        config_path = path / ".git" / "config"
        if config_path.exists():
            return config_path
        path = path.parent

    raise FileNotFoundError(
        f"Git config file '.git/config' not found in"
        f" {original_path!r} or any its parents."
    )


def getRepositoryInfo(path=None):
    """
    Return (organization, repository) tuple from .git/config file.
    """
    path = pathlib.Path(path or pathlib.Path.cwd())

    parser = configparser.ConfigParser()
    parser.read(findGitConfigFile(path))

    # Pick the first remote with a URL supplying a github org & repo.
    for section in parser.sections():
        if not section.startswith("remote"):
            continue
        info = urllib.parse.urlparse(parser[section].get("url"))  # OK if url is None
        if info.path.startswith("git@github.com:"):  # git@github.com:org/repo.git
            org, repo = info.path.rstrip(".git").split(":")[-1].split("/")
            return org, repo
        elif info.netloc == "github.com":  # https://github.com/org/repo
            org, repo = info.path.lstrip("/").rstrip(".git").split("/")
            return org, repo
    
    raise ValueError(f"No GitHub info found: {path!r}")


def get_release_info(token, base_tag_name, head_branch_name, milestone_name):
    """Mine the Github API for information about this release."""
    organization_name, repository_name = getRepositoryInfo()
    gh = github.Github(token)  # GitHub Personal Access Token

    user = gh.get_user(organization_name)
    logger.debug(f"user: {user}")

    repo = user.get_repo(repository_name)
    logger.debug(f"repo: {repo}")

    milestone = None
    for m in repo.get_milestones(state="all"):
        if m.title == milestone_name:
            milestone = m
    if milestone is None:
        msg = f"Could not find milestone: {milestone_name}"
        logger.error(msg)
        raise ValueError(msg)
    logger.debug(f"milestone: {milestone}")

    compare = repo.compare(base_tag_name, head_branch_name)
    logger.debug(f"compare: {compare}")

    commits = {c.sha: c for c in compare.commits}
    logger.debug(f"# commits: {len(commits)}")

    tags = {}
    earliest = None
    for t in repo.get_tags():
        if t.commit.sha in commits:
            tags[t.name] = t
        elif t.name == base_tag_name:
            commit = repo.get_commit(t.commit.sha)
            dt = commit.last_modified_datetime
            earliest = min(dt, earliest or dt)
    logger.debug(f"# tags: {len(tags)}")

    pulls = {
        p.number: p for p in repo.get_pulls(state="closed") if p.closed_at > earliest
    }
    logger.debug(f"# pulls: {len(pulls)}")

    issues = {
        i.number: i
        for i in repo.get_issues(milestone=milestone, state="closed")
        if ((milestone is not None or i.closed_at > earliest) and i.number not in pulls)
    }
    logger.debug(f"# issues: {len(issues)}")

    return repo, milestone, tags, pulls, issues, commits


def parse_command_line():
    """Command line argument parser."""
    doc = __doc__.strip()
    parser = argparse.ArgumentParser(description=doc)

    help_text = "name of tag to start the range"
    parser.add_argument("base", action="store", help=help_text)

    help_text = "name of milestone"
    parser.add_argument("milestone", action="store", help=help_text)

    parser.add_argument(
        "token",
        action="store",
        help=("personal access token " "(see: https://github.com/settings/tokens)"),
    )

    help_text = "name of tag, branch, SHA to end the range"
    help_text += ' (default="master")'
    parser.add_argument(
        "--head",
        action="store",
        dest="head",
        nargs="?",
        help=help_text,
        default="master",
    )

    return parser.parse_args()


def report(title, repo, milestone, tags, pulls, issues, commits):
    """Print results to stdout."""
    hbar = "-" * 3
    print(f"## {title}")
    print("")
    print(f"* **date/time**: {datetime.datetime.now()}")
    # just a suggestion, the latest release
    rr = repo.get_releases()
    print(f"* **release**: []({rr[0].html_url})")
    print(f"* **documentation**: {repo.homepage}")
    if milestone is not None:
        print(f"* **milestone**: [{milestone.title}]({milestone.url})")
        print("")
    print("section | quantity")
    print(hbar, " | ", hbar)
    print(f"[New Tags](#tags) | {len(tags)}")
    print(f"[Pull Requests](#pull-requests) | {len(pulls)}")
    print(f"[Issues](#issues) | {len(issues)}")
    print(f"[Commits](#commits) | {len(commits)}")
    print("")
    print("### Tags")
    print("")
    if len(tags) == 0:
        print("-- none --")
    else:
        print("tag | date | commit")
        print(hbar, " | ", hbar, " | ", hbar)

        def sorter(item):
            tag = item[1]
            commit = repo.get_commit(tag.commit.sha)
            return commit.last_modified_datetime

        for k, tag in sorted(tags.items(), reverse=True, key=sorter):
            commit = repo.get_commit(tag.commit.sha)
            when = commit.last_modified_datetime.strftime("%Y-%m-%d")
            base_url = tag.commit.html_url
            tag_url = "/".join(base_url.split("/")[:-2] + ["releases", "tag", k])
            print(
                f"[{k}]({tag_url})"
                f" | {when}"
                f" | [{tag.commit.sha[:7]}]({tag.commit.html_url})"
            )
    print("")
    print("### Pull Requests")
    print("")
    if len(pulls) == 0:
        print("-- none --")
    else:
        print("pull request | date | state | title")
        print(hbar, " | ", hbar, " | ", hbar, " | ", hbar)
        for k, pull in sorted(pulls.items(), reverse=True):
            state = {True: "merged", False: "closed"}[pull.merged]
            when = pull.closed_at.isoformat(sep=" ").split()[0]
            print(
                f"[#{pull.number}]({pull.html_url})"
                f" | {when}"
                f" | {state}"
                f" | {pull.title}"
            )
    print("")
    print("### Issues")
    print("")
    if len(issues) == 0:
        print("-- none --")
    else:

        def isorter(o):
            k, v = o
            logger.debug("[closed: %s] %d %s", v.closed_at, k, v.title)
            return v.closed_at

        print("issue | date | label(s) | title")
        print(hbar, " | ", hbar, " | ", hbar, " | ", hbar)
        for k, issue in sorted(issues.items(), key=isorter, reverse=True):
            if k not in pulls:
                when = issue.closed_at.strftime("%Y-%m-%d")
                labels = ", ".join([_label.name for _label in issue.labels])
                print(
                    f"[#{issue.number}]({issue.html_url})"
                    f" | {when}"
                    f" | {labels}"
                    f" | {issue.title}"
                )
    print("")
    print("### Commits")
    print("")
    if len(commits) == 0:
        print("-- none --")
    else:

        def csorter(o):
            k, v = o
            ts = v.raw_data["commit"]["committer"]["date"]
            logger.debug("[closed: %s] %s", ts, k)
            return v.raw_data["commit"]["committer"]["date"]

        print("commit | date | message")
        print(hbar, " | ", hbar, " | ", hbar)
        for k, commit in sorted(commits.items(), key=csorter, reverse=True):
            message = commit.commit.message.splitlines()[0]
            when = commit.raw_data["commit"]["committer"]["date"].split("T")[0]
            print(f"[{k[:7]}]({commit.html_url}) | {when} | {message}")


def main(base=None, head=None, milestone=None, token=None, debug=False):
    """Command-line application program."""
    if debug:
        base_tag_name = base
        head_branch_name = head
        milestone_name = milestone
        logger.setLevel(logging.DEBUG)
    else:
        cmd = parse_command_line()
        base_tag_name = cmd.base
        head_branch_name = cmd.head
        milestone_name = cmd.milestone
        token = cmd.token
        logger.setLevel(logging.WARNING)

    info = get_release_info(token, base_tag_name, head_branch_name, milestone_name)
    # milestone, repo, tags, pulls, issues, commits = info
    report(milestone_name, *info)


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
