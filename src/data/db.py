"""Deal with data content.

"""

from typing import Dict

import tinydb
from tinydb import TinyDB

import src.constants as cte
import src.data.reducto_process as rp

Report = Dict[str, Dict[str, int]]
# DB_PATH = pathlib.Path('.').resolve() / 'data' / 'processed' / 'db.json'

# db = TinyDB(DB_PATH, sort_keys=True, indent=4)
#
# reducto_reports_table = db.table('reducto_reports')


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



class DBStore:
    """
    Deal with db interaction in this class

    Examples
    --------
    >>> dbs = DBStore()
    """
    def __init__(self):
        self._db = TinyDB(cte.DB_PATH, sort_keys=True, indent=4)

    def __repr__(self):
        return type(self).__name__ + f"({self._db})"

    @property
    def db(self) -> TinyDB:
        return self._db

    @property
    def reducto_reports_table(self) -> tinydb.database.Table:
        """Returns the table containing the reducto reports. """
        return self.db.table('reducto_reports')

    @property
    def reducto_timing_table(self) -> tinydb.database.Table:
        """Returns the table containing the reducto timing.
        Contains the time in seconds reducto took to run.
        """
        return self.db.table('reducto_timing')

    @property
    def reducto_status_table(self) -> tinydb.database.Table:
        """Returns the table containing the reducto reports.
        Contains the status of the library. If was already detected, and
        in that case if worked or not.
        """
        return self.db.table('reducto_status')

    def insert_reducto_report(self, report: Report) -> None:
        """Insert a register in the corresponding table.

        Parameters
        ----------
        report : dict
            Reducto report.

        Examples
        --------
        >>> import src.data.reducto_process as rp
        >>> report = rp.read_reducto_report('click')
        >>> dbs.insert_reducto_reports(report)
        """
        self.reducto_reports_table.insert(report)

    def insert_reducto_timing(self, timing: Dict[str, float]) -> None:
        """Insert a register in the corresponding table.

        Parameters
        ----------
        timing : float
            Dict with package name and seconds elapsed during the process.

        Examples
        --------
        >>> import src.data.reducto_process as rp
        >>> dbs.insert_reducto_reports({'click': 2.1})
        """
        self.reducto_timing_table.insert(timing)

    def insert_reducto_status(self, status: Dict[str, bool]) -> None:
        """Insert a register in the corresponding table.

        Parameters
        ----------
        status : Dict[str, str]
            {'click': True}, the package worked properly.
            {'click': False}, something failed.

        Examples
        --------
        >>> import src.data.reducto_process as rp
        >>> dbs.insert_reducto_status({'click': 2.1})
        """
        self.insert_reducto_status.insert(status)

    def get_reducto_report(self, name: str) -> Report:
        """Obtain the report of a package if already inserted.

        Loops through the reducto reports table checking for the name and returns the
        whole report.

        Parameters
        ----------
        name : str
            Name of the package.

        Returns
        -------
        report : Report

        Raises
        ------
        rp.PackageNameNotFound
            If the package wasn't found.

        Examples
        --------
        >>> dbs.get_reducto_report('click')
        {'click': {'average_function_length': 11, 'blank_lines': 1518,...
        'comment_lines': 496, 'docstring_lines': 1479, 'lines': 9918,...
        'number_of_functions': 469, 'source_files': 17, 'source_lines': 6425}}
        """
        for pkg in self.reducto_reports_table.all():
            if name in pkg.keys():
                return pkg

        raise rp.PackageNameNotFound(name)

    def get_reducto_status(self, name: str) -> Report:
        """Obtain the status of a package if already inserted.

        TODO: REVIEW DOCSTRING!

        Parameters
        ----------
        name : str
            Name of the package.

        Returns
        -------
        report : Report

        Raises
        ------
        rp.PackageNameNotFound
            If the package wasn't found.

        Examples
        --------
        >>> dbs.get_reducto_report('click')
        {'click': {'average_function_length': 11, 'blank_lines': 1518,...
        'comment_lines': 496, 'docstring_lines': 1479, 'lines': 9918,...
        'number_of_functions': 469, 'source_files': 17, 'source_lines': 6425}}
        """
        for pkg in self.reducto_status_table.all():
            if name in pkg.keys():
                return pkg

        raise rp.PackageNameNotFound(name)
