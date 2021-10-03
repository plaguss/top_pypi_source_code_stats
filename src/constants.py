"""References to constant variables. """

import pathlib

# Data folders paths
# DATA_FOLDER: pathlib.Path = pathlib.Path(".").resolve() / 'data'
DATA_FOLDER: pathlib.Path = pathlib.Path(__file__).resolve().parent.parent / 'data'
EXTERNAL: pathlib.Path = DATA_FOLDER / 'external'
INTERIM: pathlib.Path = DATA_FOLDER / 'interim'
DISTRIBUTIONS: pathlib.Path = INTERIM / 'distributions'
REDUCTO_REPORTS: pathlib.Path = INTERIM / 'reducto_reports'
PROCESSED: pathlib.Path = DATA_FOLDER / 'processed'
RAW: pathlib.Path = DATA_FOLDER / 'raw'

# Database path for reducto
DB_PATH: pathlib.Path = PROCESSED / 'db.json'
# Database path for libraries.io info
DB_LIBRARIES_PATH: pathlib.Path = PROCESSED / 'db_libraries.json'

# Reducto table
REDUCTO_TABLE = pathlib.Path = PROCESSED / 'reducto_reports.csv'

REDUCTO_TABLE_ROOT = pathlib.Path = DATA_FOLDER.parent / 'reducto_reports.csv'
DOWNLOADS_PER_PACKAGE_ROOT = pathlib.Path = DATA_FOLDER.parent / 'downloads_per_package.json'
