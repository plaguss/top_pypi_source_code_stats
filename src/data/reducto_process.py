"""Contains the functionalities to install the libraries and run reducto on them.
"""

import difflib
from typing import (
    List,
    Union
)
import pathlib
import sys
import subprocess
import shutil
import logging
import json

import reducto.package as pkg
import reducto.src as src_
import reducto.reports as rp

import src.constants as cte


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PackageNameNotFound(Exception):
    """Error raised when a package could not be found for the distributions
    installed via pip.
    """
    def __init__(self, package):
        self.package = package
        self.msg: str = "Package couldn't be found"
        super().__init__(self.msg)

    def __str__(self):
        return f"{self.msg}: {self.package}"


def install(
        package: Union[pathlib.Path, str],
        target: pathlib.Path = cte.DISTRIBUTIONS
) -> None:
    r"""Installs a package in a given target.

    Tries to install a package using pip.

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

    Examples
    --------
    >>> install(cte.RAW / 'black-21.8b0')

    or

    >>> install('black')
    """
    if isinstance(target, pathlib.Path):
        if not target.is_dir():
            target.mkdir()

    args: List[str] = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--no-deps",
        "--upgrade",  # During test, overwrite if already present
        "-t",
        str(target),
        str(package),
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
    candidates : List[pathlib.Path]
        List of packages contained in a distribution.
    """
    candidates: List[pathlib.Path] = []
    for path in cte.DISTRIBUTIONS.iterdir():
        try:
            if not pkg.Package.validate(path):
                candidates.append(path)
        except pkg.PackageError:
            try:
                if not src_.SourceFile.validate(path):
                    candidates.append(path)
            except src_.SourceFileError as e:
                # One last attempt in case an inner package like in google-auth is found:
                # See package definition for:
                # https://pypi.org/project/google-auth/
                if path.is_dir():
                    for subpath in path.iterdir():
                        try:
                            if not pkg.Package.validate(subpath):
                                candidates.append(subpath)
                        except pkg.PackageError:
                            pass
        #
        # except Exception as exc:
        #     logger.warning('No packages where found')

    return candidates


def find_package(package: str) -> pathlib.Path:
    r"""After installing a package, find the directory/file containing the code to be
    parsed by reducto.

    A package may contain:
    - A single directory with the same name as pip install <PACKAGE>
    - Multiple files with one of them being the same name as the installed package.
        pip install black.
    - One or more packages, i.e.
        pip install PyYAML

    TODO:
        Needs testing!
        Use
        difflib.get_close_matches('black', ['black', 'black_primer', 'blackd', 'blib2to3'])
        >>> difflib.get_close_matches('yaml', ['PyYAML'])
        []
        >>> difflib.get_close_matches('yaml', ['PyYAML'.lower()])
        ['pyyaml']

    Parameters
    ----------
    package : str
        Name of the package as stored top-pypi-packages.

    Returns
    -------
    package : pathlib.Path
        Path to be passed to run_reducto.

    Raises
    ------
    PackageNameNotFound
        When a name could not be matched according to the names expected.

    Examples
    --------
    >>> find_package('click')
    PosixPath('/home/agustin/github_repos/top_pypi_source_code_stats/data/interim/distributions/click')
    """
    candidates: List[pathlib.Path] = distribution_candidates()
    candidates_lower = [candidate.stem.lower() for candidate in candidates]
    matches = difflib.get_close_matches(package, candidates_lower)
    if len(matches) > 0:
        idx: int = candidates_lower.index(matches[0])
        return candidates[idx]
    else:
        raise PackageNameNotFound(package)


def run_reducto(
        target: pathlib.Path,
        output_path: pathlib.Path = cte.REDUCTO_REPORTS
) -> None:
    """Run reducto on a distribution package and store the report on data/interim.

    Parameters
    ----------
    target : pathlib.Path
        Path target to execute reducto against.
    output_path : pathlib.Path
        Path where the report from reducto is stored. Defaults to cte.REDUCTO_REPORTS

    Examples
    --------
    >>> target = find_package('click')
    >>> run_reducto(target)
    """
    if not output_path.is_dir():
        output_path.mkdir()

    output: str = str(output_path / (target.stem + '.json'))
    args: List[str] = [
        "reducto",
        str(target),
        "-o",
        output
    ]
    try:
        subprocess.check_output(args)
        logger.info(f"Reducto report created: {output}")
    except subprocess.CalledProcessError as exc:
        logger.error(f"Reducto failed on: {target}")
        raise exc.output


def read_reducto_report(package: str) -> Union[rp.SourceReportType, rp.PackageReportType]:
    """Read the reducto report of a given package.

    Parameters
    ----------
    package : str
        Name of the package to download.

    Returns
    -------
    report : dict
        reducto package report.

    Raises
    ------
    FileNotFoundError
        If the file doesn't exists.

    Examples
    --------
    >>> read_reducto_report('click')
    {'click': {'lines': 9918, 'number_of_functions': 469,...}
    """
    report_path: pathlib.Path = cte.REDUCTO_REPORTS / (package + '.json')

    if report_path.is_file():
        with open(report_path, 'r') as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"reducto report doesn't exists: {report_path}")


def clean_folder(path: pathlib.Path) -> None:
    """Remove every file/folder in the given path.

    Parameters
    ----------
    path : pathlib.Path
        Path to be cleaned.

    Examples
    --------
    >>> clean_folder(cte.DISTRIBUTIONS)
    """
    for p in path.iterdir():
        if p.is_file():
            p.unlink()
        elif p.is_dir():
            shutil.rmtree(p)

    logger.info(f'Everything removed on: {path}')
