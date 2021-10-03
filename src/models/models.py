"""

"""

from typing import List

import numpy as np
import pandas as pd
import statsmodels.api as sm

import src.features.build_features as bf
import src.data.download as dwn


def reducto_explain_downloads(
        log_y: bool = False,
        log_x: bool = True,
        drop_columns: List[str] = None
) -> None:
    """Linear regression model to explain the total number of downloads per package.

    Given the variables source_lines, docstring_lines, comment_lines and blank_lines
    are a perfectly collinear, one of them must be removed, in this case blank_lines
    is chosen to be removed.

    Prints the model summary.

    Parameters
    ----------
    log_y : bool
        Apply logs to endogenous variable.
    log_x : bool
        Apply logs to columns lines, average_function_length, number_of_functions
        and source_files.
    drop_columns : List[str]
        Columns to be dropped from explanatory variables.
        Due to high multicollinearity some variables may be better removed
    """
    guide = bf.get_reducto_reports_relative(log=log_x)
    columns_ = [
        'lines', 'source_lines', 'docstring_lines',
        'comment_lines', 'average_function_length', 'number_of_functions',
        'source_files'
    ]
    guide = guide[columns_]
    downloads = dwn.get_downloads_per_package(guide=list(guide.index))
    y = list(downloads.values())
    X = guide.values
    X = sm.add_constant(X, prepend=True)
    columns = ['constant']
    columns.extend(list(guide.columns))
    X = pd.DataFrame(X, columns=columns)

    if drop_columns is not None:
        X.drop(drop_columns, axis=1, inplace=True)

    if log_y:
         y = np.log(y)

    # Fit and summarize OLS model
    mod = sm.OLS(y, X)
    res = mod.fit(cov_type='HC1')
    print(res.summary())
    return res
