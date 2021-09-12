"""Contains the functionalities to install the libraries and run reducto on them.
"""


from typing import List
import pathlib
import sys
import subprocess

import reducto.package as pkg
import reducto.src as src_

import src.constants as cte


def install(
        package: pathlib.Path,
        target: pathlib.Path = cte.INTERIM
) -> None:
    r"""Installs a package in a given target.

    Tries to install a package using pip.
    TODO:
        Installing this way needs a setup.py
        - Needs a check for flit, poetry and other libraries
        In tat case pip_install through pypi

    Runs a command like the following:
    python -m pip install --no-deps --target
    /home/agustin/github_repos/top_pypi_source_code_stats/data/interim/
    /home/agustin/github_repos/top_pypi_source_code_stats/data/raw/black-21.8b0/

    Parameters
    ----------
    package : pathlib.Path
        Package to install. dist-info.
    target : pathlib.Path
        Directory where the package is installed.

    Returns
    -------
    None

    Examples
    --------
    >>> install(str(cte.RAW / 'black-21.8b0'))
    """
    args: List[str] = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--no-deps",
        "--upgrade",  # During test, overwrite if already present
        "-t",
        target,
        package,
    ]
    try:
        subprocess.check_output(args)
    except subprocess.CalledProcessError as exc:
        raise exc.output


def distribution_candidates() -> List[pathlib.Path]:
    """Obtain the distribution candidates to be passed to find_distribution.

    Check possible candidates to be fed to reducto

    Returns
    -------

    """
    candidates: List[pathlib.Path] = []
    for path in cte.INTERIM.iterdir():
        try:
            if not pkg.Package.validate(path) or not src_.SourceFile.validate(path):
                candidates.append(path)
        except (pkg.PackageError, src_.SourceFileError) as e:
            pass

    return candidates


def find_distribution(path: str) -> pathlib.Path:
    """After installing a package, find the directory/file containing the code to be
    parsed by reducto.

    A package may contain:
    - A single directory with the same name as pip install <PACKAGE>
    - Multiple files with one of them being the same name as the installed package.
        pip install black.
    - One or more packages, i.e.
        pip install PyYAML

    TODO:
        Use
        difflib.get_close_matches('black', ['black', 'black_primer', 'blackd', 'blib2to3'])

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
