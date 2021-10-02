"""

"""

import numpy as np
import pandas as pd
import statsmodels.api as sm

import src.features.build_features as bf
import src.data.download as dwn


def reducto_explain_downloads(log_y: bool = False, log_x: bool = True) -> None:
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
    """
    guide = bf.get_reducto_reports_relative(log=log_x)
    columns_ = [
        'lines', 'source_lines', 'docstring_lines',
        'comment_lines', 'average_function_length', 'number_of_functions',
        'source_files'
    ]
    guide = guide[columns_]
    y = dwn.get_downloads_per_package(guide).values.flatten()
    X = guide.values
    X = sm.add_constant(X, prepend=True)
    columns = ['constant']
    columns.extend(list(guide.columns))
    X = pd.DataFrame(X, columns=columns)

    if log_y:
         y = np.log(y)

    # Fit and summarize OLS model
    mod = sm.OLS(y, X)
    res = mod.fit()
    print(res.summary())
