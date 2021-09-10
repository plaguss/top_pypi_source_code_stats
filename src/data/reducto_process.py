"""Contains the functionalities to install the libraries and run reducto on them.
"""


from typing import List
import pathlib
import sys
import subprocess


def install_to(target: pathlib.Path, package: pathlib.Path) -> None:
    r"""Installs a package in a given target.

    Tries to install a package using pip.
    TODO:
        Installing this way needs a setup.py
        - Needs a check for flit, poetry and other libraries

    Runs a command like the following:
    python -m pip install --no-deps --target
    /home/agustin/github_repos/top_pypi_source_code_stats/data/interim/
    /home/agustin/github_repos/top_pypi_source_code_stats/data/raw/black-21.8b0/

    Parameters
    ----------
    target
    package

    Returns
    -------

    Examples
    --------
    >>>
    """
    args: List[str] = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--no-deps",
        "-t",
        target,
        package,
    ]
    try:
        subprocess.run(args)
    except subprocess.CalledProcessError as exc:
        print(f"{package} couldn't be installed due to:")
        raise exc


def find_distribution(path: str) -> pathlib.Path:
    """After installing a package, find the directory/file containing the code to be
    parsed by reducto.

    A package may contain:
    - A single directory with the same name as pip install <PACKAGE>
    - Multiple files with one of them being the same name as the installed package.
        pip install black.
    - One or more packages, i.e.
        pip install PyYAML

    Parameters
    ----------
    path : str
        Path where the candidates are to be found.

    Returns
    -------

    """
    pass


def run_reducto(target: str) -> None:
    """Run reducto on a distribution package and store the report on data/interim.

    Returns
    -------

    """
    pass


def insert_reports():
    """Insert the reducto report of the library to db.json.

    Returns
    -------

    """
    pass


def remove_reports():
    """Remove after a process is done.

    Returns
    -------

    """
    pass
