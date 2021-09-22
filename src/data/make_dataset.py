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
from time import time
from mpire import WorkerPool
from os import cpu_count
from functools import partial

import src.data.download as dwn
import src.constants as cte
import src.data.reducto_process as rp
import src.data.db as db

log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_fmt)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


workers = cpu_count() - 1


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
    subset = packages[start:stop]  # Maybe extract to a small list.

    # Fails to run in parallel, just run it for the moment...
    for pkg in subset:
        extract_reducto(pkg, dbs)

    # partial_reducto = partial(extract_reducto, database=dbs)
    # with WorkerPool(n_jobs=workers) as pool:
    #     results = pool.map(partial_reducto, subset, progress_bar=True)


def extract_reducto(pkg: str = None, database: db.DBStore = None) -> None:
    """Extracts the reducto report of a python package.

    Downloads, installs, grabs the content and removes everything when finished.

    Parameters
    ----------
    pkg : str
        Name of the package, as obtained from the list of get dwn.get_top_packages.
    database : db.DBStore
        Instance of DBStore.
    """
    try:
        database.get_reducto_status(pkg)
    except rp.PackageNameNotFound:
        logger.info(f"Skipping: {pkg}, already downloaded.")
        return

    # 1) Download the package
    pkg_path: pathlib.Path = dwn.download_and_extract(pkg, cte.RAW)
    # 2) Install it
    try:
        try:
            rp.install(pkg_path)
        except Exception as exc:
            # Installing from the download failed, install directly from pypi.
            rp.install(pkg)
        finally:
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
        return

    # 4) Run reducto on it.
    if target:
        try:
            tstart = time()
            rp.run_reducto(target)
            # Check time running
            database.insert_reducto_timing({pkg: time() - tstart})
            rp.clean_folder(cte.DISTRIBUTIONS)
            logger.info(f"Reducto run on: {pkg}.")
        except rp.PackageNameNotFound:
            # TODO: Register to db
            logger.error(f"{pkg} could not be found.")
            return
    else:
        database.insert_reducto_status({pkg: False})
        logger.error(f"find_package failed on {pkg} .")
        return

    # 5) Read report:
    report: db.Report = rp.read_reducto_report(target.stem)
    # report: db.Report = rp.read_reducto_report(pkg)
    # 6) Insert to db.
    database.insert_reducto_report(report)
    # 7) Clean folders after.
    rp.clean_folder(cte.REDUCTO_REPORTS)

    # 8) Insert status
    database.insert_reducto_status({pkg: True})

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
