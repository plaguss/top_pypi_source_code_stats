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
    return pd.read_csv(cte.REDUCTO_TABLE, index_col=0)


def get_reducto_reports_table_no_outliers() -> pd.DataFrame:
    """Remove from the initial table the packages with more than 1e6 lines of code,
    and those with average function length smaller than 200

    Returns
    -------
    data : pd.DataFrame
    """
    table = get_reducto_reports_table()
    # Packages with less than a million lines of code
    no_outliers = table[table['lines'] < 1e6]
    no_outliers = no_outliers[no_outliers['average_function_length'] < 200]
    return no_outliers


def get_reducto_reports_relative() -> pd.DataFrame:
    """From the table without outliers, returns the number of lines as a percentage of
    the total number of lines (for the variables

    Returns
    -------

    """
    no_outliers = get_reducto_reports_table_no_outliers()
    total_lines = no_outliers['lines']
    no_outliers[['source_lines', 'blank_lines', 'docstring_lines', 'comment_lines']] = \
        no_outliers[
            ['source_lines', 'blank_lines', 'docstring_lines', 'comment_lines']].divide(
            total_lines, axis=0
        )
    return no_outliers

