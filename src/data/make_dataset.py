"""
After installing the package (pip install -e .)
Example run:
$ reducto_reports --stop=1

TODO:
    - Add logs of the process.
    - Ensure unnecesary data is cleaned after.
    - Store the total time of the process in the database.

Status:
    - 3999 packages
    - failed 350, reasons:
        - find_package: 150
        - install: 123
        - reducto: 77

"""

# -*- coding: utf-8 -*-
from typing import List

import pathlib

import logging
from pathlib import Path
# from dotenv import find_dotenv, load_dotenv
from time import time
from os import cpu_count

import tqdm
import click
import pandas as pd
from tinydb import Query

import src.data.download as dwn
import src.constants as cte
import src.data.reducto_process as rp
import src.data.db as db

LOGFILE = 'reducto3.log'  # filename for the logs

log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(
    filename=str(cte.DATA_FOLDER / LOGFILE),
    level=logging.INFO,
    format=log_fmt
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


workers = cpu_count() - 1


def update_dict_key(dictionary: db.Report, key: str) -> db.Report:
    """Function to update the package name of a report.

    Some google packages have misleading package names, for example
    protobuf or google-auth. Use this function to keep the original name
    when inserting to db.

    Parameters
    ----------
    dictionary : db.Report
        Report obtained from reducto.
    key : str
        Name to update the package.

    Returns
    -------
    updated : db.Report
        Updates the key in the report.

    Examples
    --------
    >>> report = {'auth': {'lines': 9346, 'number_of_functions': 309...}}
    >>> update_dict_key(report, 'google_auth')
    {'google_auth': {'lines': 9346, 'number_of_functions': 309...}}
    """
    old_key: str = [k for k in dictionary.keys()][0]
    dictionary[key] = dictionary[old_key]
    del(dictionary[old_key])
    return dictionary


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
    for pkg in tqdm.tqdm(subset):
        print(f'extract reducto: {pkg}')
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
        check = database.get_reducto_status(pkg)
        if check[pkg]:
            report = database.get_reducto_report(pkg)
            database.insert_reducto_report(pkg,report)
            database.insert_reducto_status(pkg, True, "")
            logger.info(f"Skipping, package already downloaded: {pkg}.")
            return
        else:
            logger.info(f"Errored package, needs review: {pkg}.")
    except rp.PackageNameNotFound:
        # Package not downloaded, keep going.
        pass

    # Install directly using pip:
    try:
        rp.install(pkg)
        rp.clean_folder(cte.RAW)
        logger.info(f"{pkg} installed.")

    except Exception as exc:
        logger.error(f"{pkg} could not be installed due to: {exc}.", exc_info=True)
        # TODO: check if already inserted as False
        database.insert_reducto_status(pkg, True, "install")
        return

    # 3) find the package to be passed to reducto.
    target = None
    try:
        try:
            target: pathlib.Path = rp.find_package(pkg)
        except rp.PackageNameNotFound:
            logger.info(
                f"find_packages failed on: {pkg} try with distribution_candidates."
            )
            target: pathlib.Path = rp.distribution_candidates()[0]
    except IndexError:
        logger.error(
            f"{pkg} could not be found, on find_package or distribution_candidates",
            exc_info=True
        )
        database.insert_reducto_status(pkg, False, "find_package")

        return

    # 4) Run reducto on it.
    if target:
        try:
            tstart = time()
            rp.run_reducto(target)
            # Check time running
            database.insert_reducto_timing(pkg, time() - tstart)
            rp.clean_folder(cte.DISTRIBUTIONS)
            logger.info(f"Reducto run on: {pkg}.")
        except rp.PackageNameNotFound:
            # TODO: Register to db
            logger.error(f"{pkg} could not be found, running reducto.", exc_info=True)
            database.insert_reducto_status(pkg, False, "reducto_name")
            return
        except Exception as exc:
            logger.error(f"reducto failed on: {pkg}, error: {exc}", exc_info=True)
            database.insert_reducto_status(pkg, False, "reducto_error")
            return
    else:
        database.insert_reducto_status(pkg, False, "find_package")
        logger.error(f"find_package failed on {pkg} .", exc_info=True)
        return

    # 5) Read report:
    report: db.Report = rp.read_reducto_report(target.stem)
    # 6) Insert to db.
    report = update_dict_key(report, pkg)
    database.insert_reducto_report(pkg, report)
    # 7) Clean folders after.
    rp.clean_folder(cte.REDUCTO_REPORTS)

    # 8) Insert status
    database.insert_reducto_status(pkg, True, "")

    logger.info(f"Process finished: {pkg}.")


@make_dataset.command()
@click.option(
    '--output_filename',
    default=cte.PROCESSED / 'reducto_reports.csv',
    show_default=True,
    help='Path to write the file'
)
def reducto_table(output_filename: pathlib.Path = cte.PROCESSED / 'reducto_reports.csv'):
    """Creates a csv representing the table of reducto reports. """
    dbs: db.DBStore = db.DBStore()
    table_dict = {}
    columns = [
        'lines', 'source_lines', 'blank_lines', 'docstring_lines', 'comment_lines',
        'average_function_length', 'number_of_functions', 'source_files'
    ]
    for report in dbs.reducto_reports_table.all():
        name = report["name"]
        if name == 'filelock' or name == 'recordclass':
            # FIXME: These packages failed to obtain the report, must be checked
            pass
        else:
            values = list(report["report"].values())
            # If a package has no source_files, write one by default, is a single script
            table_dict[name] = [val.get(col, 1) for col in columns for val in values]

    table = pd.DataFrame.from_dict(table_dict, orient='index', columns=columns)
    table.to_csv(output_filename)


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
