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

import src.data.download as dwn
import src.constants as cte
import src.data.reducto_process as rp
import src.data.db as db


logger = logging.getLogger(__name__)


@click.command()
@click.option(
    '--stop',
    default=-1,
    show_default=True,
    help='Number of packages to download.'
)
def reducto_reports(stop: int = -1):
    """Downloads every package in top-pypi-packages-365-days.json, extracts the reducto
    report and inserts it to the db.json, and then removes the downloaded package.

    Parameters
    ----------
    stop : int
        Index of the package to stop the process.
        For debugging purposes. Defaults to -1 (downloads every package in the list).
        If set to 2, downloads the first 2 packages.

    Returns
    -------

    """
    dbs: db.DBStore = db.DBStore()
    # Download the packages.
    packages: List[str] = dwn.get_top_packages()
    for pkg in packages[:stop]:
        # 1) Download the package
        pkg_path: pathlib.Path = dwn.download_and_extract(pkg, cte.RAW)
        # 2) Install it
        try:
            rp.install(pkg_path)
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
            except rp.PackageNameNotFound:
                # TODO: Register to db
                logger.error(f"{pkg} could not be found.")

        # 5) Read report:
        report: db.Report = rp.read_reducto_report(pkg)
        # 6) Insert to db.
        dbs.insert_reducto_report(report)
        # 7) Clean folders after.
        rp.clean_folder(pkg_path)


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
