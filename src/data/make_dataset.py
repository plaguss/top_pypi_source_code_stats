"""
After installing the package (pip install -e .)
Example run:
$ reducto_reports --stop=1

TODO:
    - Add logs of the process.
    - Ensure unnecesary data is cleaned after.
    - Store the total time of the process in the database.

"""

# -*- coding: utf-8 -*-
from typing import List

import pathlib

import click
import logging
from pathlib import Path
# from dotenv import find_dotenv, load_dotenv
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from os import cpu_count

import src.data.download as dwn
import src.constants as cte
import src.data.reducto_process as rp
import src.data.db as db

log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_fmt)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


workers = cpu_count() - 1


# with ThreadPoolExecutor(max_workers=workers) as executor:
#     bound_downloader = partial(get_package, directory=directory)
#     for package, package_directory in executor.map(
#             bound_downloader, packages
#     ):
#         if package_directory is not None:
#             caches.append(package)
#             print(
#                 f"Package {package_directory} is created for {package}."
#             )
#
# with ThreadPoolExecutor() as executor:
#     futures = []
#     for url in wiki_page_urls:
#         futures.append(executor.submit(get_wiki_page_existence, wiki_page_url=url))
#     for future in concurrent.futures.as_completed(futures):
#         print(future.result())
#

@click.group()
def make_dataset():
    """Group command, does nothing on its own. """
    pass


@make_dataset.command()
@click.option(
    '--start',
    default=0,
    show_default=True,
    help='Start downloading from this point of the list of packages.'
)
@click.option(
    '--stop',
    default=-1,
    show_default=True,
    help='Stop downloading on this point of the list of packages.'
)
def reducto_reports(start: int = 0, stop: int = -1):
    """Downloads every package in top-pypi-packages-365-days.json, extracts the reducto
    report and inserts it to the db.json, and then removes the downloaded package.

    Parameters
    ----------
    start : int
        Index of the package to start the process.
        For debugging purposes. Defaults to 0 (downloads from the first package
        in the list).
    stop : int
        Index of the package to stop the process.
        For debugging purposes. Defaults to -1 (downloads until the last).
    """
    dbs: db.DBStore = db.DBStore()
    # Download the packages.
    packages: List[str] = dwn.get_top_packages()
    for pkg in packages[start:stop]:
        extract_reducto(pkg, dbs)


def extract_reducto(pkg: str, database: db.DBStore) -> None:
    """Extracts the reducto report of a python package.

    Downloads, installs, grabs the content and removes everything when finished.

    Parameters
    ----------
    pkg : str
        Name of the package, as obtained from the list of get dwn.get_top_packages.
    database : db.DBStore
        Instance of DBStore.
    """
    # 1) Download the package
    pkg_path: pathlib.Path = dwn.download_and_extract(pkg, cte.RAW)
    # 2) Install it
    try:
        rp.install(pkg_path)
        rp.clean_folder(cte.RAW)
        logger.info(f"{pkg} installed.")
    except Exception as exc:
        # TODO: Register to db
        logger.error(f"{pkg_path} could not be installed due to: {exc}.")

    # 3) find the package to be passed to reducto.
    target = None
    try:
        target: pathlib.Path = rp.find_package(pkg)
    except rp.PackageNameNotFound:
        # TODO: Register to db
        logger.error(f"{pkg} could not be found.")

    # 4) Run reducto on it.
    if target:
        try:
            rp.run_reducto(target)
            rp.clean_folder(cte.DISTRIBUTIONS)
            logger.info(f"Reducto run on: {pkg}.")
        except rp.PackageNameNotFound:
            # TODO: Register to db
            logger.error(f"{pkg} could not be found.")

    # 5) Read report:
    report: db.Report = rp.read_reducto_report(pkg)
    # 6) Insert to db.
    database.insert_reducto_report(report)
    # 7) Clean folders after.
    rp.clean_folder(cte.REDUCTO_REPORTS)

    logger.info(f"Process finished: {pkg}.")


@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger.info('making final data set from raw data')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    # load_dotenv(find_dotenv())

    main()
