"""Deal with data content.

"""

from typing import Dict
import pathlib

from tinydb import TinyDB, Query

DB_PATH = pathlib.Path('.').resolve() / 'data' / 'processed' / 'db.json'

db = TinyDB(DB_PATH, sort_keys=True, indent=4)

reducto_reports_table = db.table('reducto_reports')


# db.insert({'type': 'peach', 'count': 3})
# db.insert({'type': 'apple', 'count': 2})
#
#
# TABLE_DOWNLOADS = 'downloads'
# Fruit = Query()
# db.search(Fruit.type == 'peach')

# downloads = db.table(TABLE_DOWNLOADS)
# name, path = download.get_package('click', download.PACKAGES_DIRECTORY)  #
# downloads.insert({'package': result[0]})
# package_info = {
#     'pypi_package': 'PATH_TO_ORIGINAL_PACKAGE',
#     'reducto_target': 'FIND_PATH_TO_SOURCE',  # Create helper function
#     'version': 'PATH_TO_ORIGINAL_PACKAGE',
#     'processed': 'BOOL',  # Whether the package is already processed or not. Remove when done
#     'reducto_stats': 'REDUCTO_EXECUTED_ON_REDUCTO_TARGET',
#     'libraries': 'OBTAINED_FROM_PYBRARIES'
# }

# example = {
#     'package_name_1': 'package_info_1',  # Obtained
#     'package_name_2': 'package_info_2',
# }


def insert_reducto_reports(report: Dict) -> None:
    """Insert the reducto report of the package to db.json.

    Parameters
    ----------
    report : Dict

    Examples
    --------
    >>> import src.data.reducto_process as rp
    >>> report = rp.read_reducto_report('click')
    >>> insert_reducto_reports(report)
    """
    reducto_reports_table.insert(report)

