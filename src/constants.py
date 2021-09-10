"""References to constant variables. """

import pathlib

# Data folders paths
DATA_FOLDER: pathlib.Path = pathlib.Path.cwd() / 'data'
EXTERNAL: pathlib.Path = DATA_FOLDER / 'external'
INTERIM: pathlib.Path = DATA_FOLDER / 'interim'
PROCESSED: pathlib.Path = DATA_FOLDER / 'processed'
RAW: pathlib.Path = DATA_FOLDER / 'raw'

# Database path
DB_PATH: pathlib.Path = PROCESSED / 'db.json'
