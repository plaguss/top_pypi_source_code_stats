"""File copied from isidentical.
https://github.com/plaguss/syntax_test_suite
"""

import json
import os
import tarfile
import traceback
import zipfile
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path
from typing import Generator, List, Literal, Optional, Tuple, Union, cast, Dict
from urllib.request import Request, urlopen, urlretrieve
import pathlib

import src.constants as cte


PYPI_INSTANCE = "https://pypi.org/pypi"
PYPI_TOP_PACKAGES = "https://hugovk.github.io/top-pypi-packages/top-pypi-packages-{days}-days.json"
# PYPI_TOP_PACKAGES_LOCAL = str(
#     pathlib.Path.cwd() / 'data' / 'external' / 'top-pypi-packages-365-days.json'
# )
PYPI_TOP_PACKAGES_LOCAL = str(cte.EXTERNAL / 'top-pypi-packages-365-days.json')

ArchiveKind = Union[tarfile.TarFile, zipfile.ZipFile]
Days = Union[Literal[30], Literal[365]]


def get_package_source(package: str, version: Optional[str] = None) -> str:
    with urlopen(PYPI_INSTANCE + f"/{package}/json") as page:
        metadata = json.load(page)

    if version is None:
        sources = metadata["urls"]
    else:
        if version in metadata["releases"]:
            sources = metadata["releases"][version]
        else:
            raise ValueError(
                f"No releases found with given version ('{version}') tag. "
                f"Found releases: {metadata['releases'].keys()}"
            )

    for source in sources:
        if source["python_version"] == "source":
            break
    else:
        raise ValueError(f"Couldn't find any sources for {package}")

    return cast(str, source["url"])


def get_archive_manager(local_file: str) -> ArchiveKind:
    if tarfile.is_tarfile(local_file):
        return tarfile.open(local_file)
    elif zipfile.is_zipfile(local_file):
        return zipfile.ZipFile(local_file)
    else:
        raise ValueError("Unknown archive kind.")


def get_first_archive_member(archive: ArchiveKind) -> str:
    if isinstance(archive, tarfile.TarFile):
        return archive.getnames()[0]
    elif isinstance(archive, zipfile.ZipFile):
        return archive.namelist()[0]


def download_and_extract(
        package: str,
        directory: Path,
        version: Optional[str] = None,
        remove_after: bool = False
) -> Path:
    """Modified to allow avoiding removing files after.

    Parameters
    ----------
    package
    directory
    version
    remove_after

    Returns
    -------

    Examples
    --------
    >>> import src.constants as cte
    >>> download_and_extract('six', cte.RAW)
    PosixPath('/home/agustin/github_repos/top_pypi_source_code_stats/data/raw/six-1.16.0')
    """
    try:
        source = get_package_source(package, version)
    except ValueError:
        return None

    print(f"Downloading {package}.")
    local_file, _ = urlretrieve(source, directory / f"{package}-src")
    with get_archive_manager(local_file) as archive:
        print(f"Extracting {package}")
        archive.extractall(path=directory)
        result_dir = get_first_archive_member(archive)
    if remove_after:
        os.remove(local_file)
    return directory / result_dir


def get_package(package: str, directory: Path, version: Optional[str] = None):
    try:
        return package, download_and_extract(package, directory, version)
    except Exception as e:
        print(f"Caught an exception while downloading {package}.")
        traceback.print_exc()
        return package, None


def get_top_packages(days: Optional[Days] = None, local: bool = True) -> List[str]:
    """Modified function to allow using local file instead of the original repository.

    Parameters
    ----------
    days
    local

    Returns
    -------
    packages : List[str]
        List of packages.

    Examples
    --------
    >>> get_top_packages()
    ['urllib3', 'six', 'botocore', 'setuptools', 'requests',...
    """
    if not local:  # original function
        with urlopen(PYPI_TOP_PACKAGES.format(days=days)) as page:
            result = json.load(page)
    else:
        with open(PYPI_TOP_PACKAGES_LOCAL, 'r') as f:
            result = json.load(f)

    return [package["project"] for package in result["rows"]]


def get_downloads_per_package(
        days: Optional[Days] = None, local: bool = True, guide: List[str] = None
) -> Dict[str, int]:
    """Modified function to allow using local file instead of the original repository.

    Parameters
    ----------
    days
    local
    guide

    Returns
    -------
    packages : List[str]
        List of packages.

    Examples
    --------
    >>> get_top_packages_and_downloads()
    {'urllib3': 30214908...}
    """
    if not local:  # original function
        with urlopen(PYPI_TOP_PACKAGES.format(days=days)) as page:
            result = json.load(page)
    else:
        with open(PYPI_TOP_PACKAGES_LOCAL, 'r') as f:
            result = json.load(f)

    if isinstance(guide, list):
        downloads = {
            package['project']: package['download_count'] for package in result["rows"]
            if package['project'] in guide
        }
    else:
        downloads = {
            package['project']: package['download_count'] for package in result["rows"]
        }

    return downloads


def get_downloads_per_package_root(guide: List[str] = None):
    """Watch get_downloads_per_package to see a guide of the function. """
    with open(cte.DOWNLOADS_PER_PACKAGE_ROOT) as f:
        data = json.load(f)

    if isinstance(guide, list):
        downloads = {k: v for k, v in data.items() if k in guide}

        return downloads
    else:
        return data


def dump_config(directory: Path, values: List[str]):
    with open(directory / "info.json", "w") as f:
        json.dump(values, f)


def read_config(directory: Path) -> List[str]:
    if (pkg_config := directory / "info.json").exists():
        with open(pkg_config) as f:
            cache = json.load(f)
        return cache
    else:
        return []


def filter_already_downloaded(
    directory: Path, packages: List[str]
) -> List[str]:
    cache = read_config(directory)
    return [package for package in packages if package not in cache]


def download_top_packages(
    directory: Path,
    days: Days = 365,
    workers: int = 24,
    limit: slice = slice(None),
):
    assert directory.exists()
    if not (directory / "info.json").exists():
        dump_config(directory, [])

    packages = get_top_packages(days)[limit]
    packages = filter_already_downloaded(directory, packages)
    caches = []
    try:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            bound_downloader = partial(get_package, directory=directory)
            for package, package_directory in executor.map(
                bound_downloader, packages
            ):
                if package_directory is not None:
                    caches.append(package)
                    print(
                        f"Package {package_directory} is created for {package}."
                    )
    finally:
        dump_config(directory, read_config(directory) + caches)


def main():
    parser = ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--days", choices=(30, 365), type=int, default=30)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument(
        "--limit",
        type=lambda limit: slice(*map(int, limit.split(":"))),
        default=slice(0, 10),
    )
    options = parser.parse_args()
    download_top_packages(**vars(options))


if __name__ == "__main__":
    main()
