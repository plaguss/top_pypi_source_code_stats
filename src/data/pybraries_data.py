"""Grab data from libraries.io
"""


from typing import Generator

import pathlib
import time

from pybraries.search import Search

import src.data.db as db


def get_librariesio_data() -> None:
    """Obtain libraries.io data corresponding to correctly obtained packages and
    insert the data to the corresponding db.

    Obtains the pacakges from db.json.

    Parameters
    ----------
    output_path : pathlib.Path
    """
    reducto_db = db.DBStore()
    libraries_db = db.DBLibraries()

    # Packages to be requested.
    packages: Generator = (pkg["name"] for pkg in reducto_db.reducto_reports_table.all())

    # Instantiate the class to generate the requests.
    search = Search()

    for i, pkg in enumerate(packages):
        print(f"package: {i}, {pkg}")
        # sourcerank (get as explanatory variables)
        # sourcerank = search.project_sourcerank(platforms='pypi', project=pkg)
        # # general info (get stars)
        # project_info = search.project(platforms='pypi', name=pkg)
        # stars = project_info['stars']
        # # Get len to obtain the number of contributors
        # contribs = search.project_contributors('pypi', pkg)
        # # Account only for the total number of contributors
        # contributors = len(contribs)
        sourcerank, stars, contributors = download_from_libraries(search, pkg)

        libraries_db.insert_sourcerank(pkg, sourcerank)
        libraries_db.insert_stars_contributors(pkg, stars, contributors)
        time.sleep(1)


def download_from_libraries(searcher, pkg: str):
    try:
        sourcerank = searcher.project_sourcerank(platforms='pypi', project=pkg)
        # general info (get stars)
        project_info = searcher.project(platforms='pypi', name=pkg)
        stars = project_info['stars']
        # Get len to obtain the number of contributors
        contribs = searcher.project_contributors('pypi', pkg)
        # Account only for the total number of contributors
        contributors = len(contribs)
        return sourcerank, stars, contributors
    except Exception as exc:
        import traceback
        traceback.print_exc()
        print("Sleep 60 seconds")
        time.sleep(60)  # Sleep for a minute
