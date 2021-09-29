"""Deal with data content.

"""
import pathlib
from typing import (
    Dict,
    List,
    Optional,
    Union
)

import tinydb
from tinydb import TinyDB, Query

import src.constants as cte

Report = Dict[str, Dict[str, int]]


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

    def insert_reducto_report(self, name: str, report: Report) -> None:
        """Insert a register in the corresponding table.

        Parameters
        ----------
        name : str
            Name of the package. For easy querying.
        report : dict
            Reducto report.

        Examples
        --------
        >>> import src.data.reducto_process as rp
        >>> report = rp.read_reducto_report('click')
        >>> dbs.insert_reducto_reports('click', report)
        """
        self.reducto_status_table.insert({"name": name, "report": report})

    def insert_reducto_timing(self, name: str, timing: float) -> None:
        """Insert a register in the corresponding table.

        Parameters
        ----------
        name : str
            Name of the package.
        timing : float
            Dict with package name and seconds elapsed during the process.

        Examples
        --------
        >>> import src.data.reducto_process as rp
        >>> dbs.insert_reducto_reports({'click': 2.1})
        """
        self.reducto_timing_table.insert({"name": name, "time": timing})

    def insert_reducto_status(self, name: str, status: bool, reason: str) -> None:
        """Insert a register in the corresponding table.

        Parameters
        ----------
        name : str
            Name of the package.
        status : bool
            Boolean determining whether the processing was correct (True), or failed
            (False)
        reason : str
            Reason if the failure, if any.
            When no failure ocurred (status is True), the reason is written as "",
            in case of failure, the reasons may be one of the following detected:
            'reducto_error', 'find_package', 'install'

        Examples
        --------
        >>> import src.data.reducto_process as rp
        >>> dbs.insert_reducto_status({'name': 'click', 'status': True, 'reason': ''})
        >>> dbs.insert_reducto_status({'name': 'futures', 'status': False, 'reason': ''})
        """
        status_report = {
            "name": name,
            "status": status,
            "reason": reason
        }

        self.reducto_status_table.insert(status_report)

    def get_reducto_report(self, name: str) -> Optional[Report]:
        """Obtain the report of a package if already inserted.

        Loops through the reducto reports table checking for the name and returns the
        whole report.

        Parameters
        ----------
        name : str
            Name of the package.

        Returns
        -------
        report : Report or None
            Report if found

        Examples
        --------
        >>> dbs.get_reducto_report('click')
        {'click': {'average_function_length': 11, 'blank_lines': 1518,...
        'comment_lines': 496, 'docstring_lines': 1479, 'lines': 9918,...
        'number_of_functions': 469, 'source_files': 17, 'source_lines': 6425}}
        """
        query = self.reducto_reports_table.search(Query().name == name)
        if len(query) > 0:
            return query[0]
        else:
            return

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
        >>> dbs.get_reducto_status('click')
        {'name': 'click', 'reason': '', 'status': True}
        """
        query = self.reducto_status_table.search(Query().name == name)
        if len(query) > 0:
            return query[0]
        else:
            return

    def get_failed_packages(self) -> List[Dict[str, Union[str, bool]]]:
        """Returns the packages that failed to be processed.
        Those packages with false in reducto_status_table.
        """
        return self.reducto_reports_table.search(Query().status == False)


class DBLibraries:
    def __init__(self, dbpath: pathlib.Path = cte.DB_LIBRARIES_PATH):
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
    def sourcerank_table(self) -> tinydb.database.Table:
        """Returns the table corresponding to sourcerank extraction from pybraries. """
        return self.db.table('sourcerank')

    @property
    def stars_contributors_table(self) -> tinydb.database.Table:
        """Returns the table corresponding stars and contributors per project. """
        return self.db.table('stars_contributors')

    def insert_sourcerank(self, name: str, sourcerank: Dict[str, int]) -> None:
        """Insert a register in the corresponding table.

        Parameters
        ----------
        name : str
            Name of the package.
        sourcerank : Dict[str, int]
            Extraction from pybraries of sourcerank data.

        Examples
        --------
        """
        report = {
            "name": name,
            "sourcerank": sourcerank
        }

        self.sourcerank_table.insert(report)

    def insert_stars_contributors(self, name: str, stars: int, contributors: int) -> None:
        """Insert a register in the corresponding table.

        Parameters
        ----------
        name : str
            Name of the package.
        stars : int
            Stars given to a project in pypi.
        contributors : int
            Total number of contributors to the project.

        Examples
        --------
        """
        report = {
            "name": name,
            "stars": stars,
            "contributors": contributors
        }

        self.stars_contributors_table.insert(report)
