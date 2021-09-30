"""Obtain different figures. """

import seaborn as sns
import matplotlib.pyplot as plt

import src.features.build_features as bf


def plot_histogram_relative_numbers() -> None:
    """Plots the histograms of the different columns. """
    tab = bf.get_reducto_reports_relative()
    columns = [
        'source_lines', 'blank_lines', 'docstring_lines', 'comment_lines'
    ]

    fig, axes = plt.subplots(1, 4, figsize=(15, 5), sharey=True)
    fig.suptitle("Distribution of relative features. ")

    for i, col in enumerate(columns):
        sns.histplot(tab[col], ax=axes[i],  kde=True)
        axes[i].set_title(col)


def plot_average_function_length():
    table = bf.get_reducto_reports_table()

    tab1 = table['average_function_length']
    tab2 = tab1[table['average_function_length'] < 50]

    columns = ['Every package (3647)', 'Packages with <50 lines in average (3596)']
    # titles = ['Every package', 'Packages with average < 50 lines.']
    fig, axes = plt.subplots(1, 2, figsize=(15, 5), sharey=True)
    fig.suptitle("Distribution of Average Function Length. ")

    for i, (col, data) in enumerate(zip(columns, [tab1, tab2])):
        sns.histplot(data, ax=axes[i],  kde=True)
        axes[i].set_title(col)
