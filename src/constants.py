"""References to constant variables. """

import pathlib

# Data folders paths
DATA_FOLDER: pathlib.Path = pathlib.Path(".").resolve() / 'data'
EXTERNAL: pathlib.Path = DATA_FOLDER / 'external'
INTERIM: pathlib.Path = DATA_FOLDER / 'interim'
DISTRIBUTIONS: pathlib.Path = INTERIM / 'distributions'
REDUCTO_REPORTS: pathlib.Path = INTERIM / 'reducto_reports'
PROCESSED: pathlib.Path = DATA_FOLDER / 'processed'
RAW: pathlib.Path = DATA_FOLDER / 'raw'

# Database path
DB_PATH: pathlib.Path = PROCESSED / 'db.json'