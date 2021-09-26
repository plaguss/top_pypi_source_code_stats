"""Deal with data content.

"""
import pathlib
from typing import (
    Dict,
    List
)

import tinydb
from tinydb import TinyDB

import src.constants as cte
import src.data.reducto_process as rp

Report = Dict[str, Dict[str, int]]


# TODO: Reminders
# Recreate db:
table_status = {
    "name": "pkg",
    "status": bool,
    "reason": "Failure or ''"
}

table_reports = {
    "name": "pkg",
    "report": "reducto_report"
}


class DBStore:
    """
    Deal with db interaction in this class

    Examples
    --------
    >>> dbs = DBStore()
    """
    def __init__(self, dbpath: pathlib.Path = cte.DB_PATH):
        """
        Parameters
        ----------
        dbpath : pathlib.Path
            path pointing to json file.
        """
        self._db = TinyDB(dbpath, sort_keys=True, indent=4)

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
        self.reducto_status_table.insert(status)

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

    def status_duplicates(self) -> List[str]:
        """Returns the names of the packages with duplicated registers. """
        from collections import Counter
        # Get a Counter of the packages in status
        ctr = Counter(
            [k for pkg in self.reducto_status_table.all() for (k, v) in pkg.items()]
        )
        return [k for k, v in ctr.items() if v > 1]

    def get_failed_packages(self) -> List[str]:
        """Returns the packages that failed to be processed.
        Those packages with false in reducto_status_table.
        """
        return [
            k for pkg in self.reducto_status_table.all() for k, v in pkg.items()
            if v is False
        ]
