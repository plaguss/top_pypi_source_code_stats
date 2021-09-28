"""
"""

import pandas as pd

import src.constants as cte


def get_reducto_reports_table() -> pd.DataFrame:
    """Obtain the table of reducto reports as a pandas dataframe.

    The index are the names of the packages and the columns are each of the variables
    obtained from reducto.

    Returns
    -------
    data : pd.DataFrame
    """
    return pd.read_csv(cte.PROCESSED / 'reducto_reports.csv', index_col=0)
