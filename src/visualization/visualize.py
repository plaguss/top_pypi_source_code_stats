"""Obtain different figures. """
import pandas as pd
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


def plot_pcs(log: bool = False):
    data = bf.get_pc(bf.get_reducto_reports_relative(log=log))
    sns.scatterplot(data=data, x='PC1', y='PC2')


def plot_clusters(data: pd.DataFrame, n_clusters: int = 2) -> None:
    from sklearn.cluster import KMeans
    from sklearn.metrics.pairwise import pairwise_distances_argmin

    k_means = KMeans(n_clusters=n_clusters, n_init=10)
    k_means.fit(data)

    fig = plt.figure(figsize=(15, 9))
    colors = ['#4EACC5', '#FF9C34']

    k_means_cluster_centers = k_means.cluster_centers_
    k_means_labels = pairwise_distances_argmin(data, k_means_cluster_centers)

    # KMeans
    ax = fig.add_subplot(1, 1, 1)
    for k, col in zip(range(n_clusters), colors):
        my_members = k_means_labels == k
        cluster_center = k_means_cluster_centers[k]
        ax.plot(data.iloc[my_members, 0], data.iloc[my_members, 1], 'w',
                markerfacecolor=col, marker='o', markersize=9, alpha=0.7)
        ax.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col,
                markeredgecolor='k', markersize=12)

    ax.set_title('KMeans')
    # ax.set_xticks(())
    # ax.set_yticks(())
    ax.set_xlabel('PC1')
    ax.set_ylabel('PC2')
    ax.grid(True)
