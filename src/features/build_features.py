"""
"""

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

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
    """Removes every package outside of 6 standard deviations from the columns
    lines, average_function_length, number_of_functions and source_files.

    Returns
    -------
    data : pd.DataFrame
    """
    table = get_reducto_reports_table()
    # Packages with less than a million lines of code
    n_std = 6
    idx1 = table['lines'] < table['lines'].std() * n_std
    idx2 = table['average_function_length'] < table['average_function_length'].std() * n_std
    idx3 = table['number_of_functions'] < table['number_of_functions'].std() * n_std
    idx4 = table['source_files'] < table['source_files'].std() * n_std

    # Remove rows with more than 6 std in any column
    no_outliers = table[idx1 * idx2 * idx3 * idx4]

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


def get_pc(data: pd.DataFrame, standardize: bool = False) -> pd.DataFrame:
    # data = get_reducto_reports_table_no_outliers()
    # pca = PCA(n_components=2).fit(data)
    # pca.explained_variance_ratio_
    if standardize:
        data = (data - data.mean()) / data.std()
    reduced_data = PCA(n_components=2).fit_transform(data)
    return pd.DataFrame(reduced_data, columns=['PC1', 'PC2'])


def number_of_clusters(data: pd.DataFrame):
    # import matplotlib.pyplot as plt

    from sklearn.metrics import silhouette_samples, silhouette_score

    range_n_clusters = [2, 3, 4, 5, 6, 7, 8]

    for n_clusters in range_n_clusters:
        # fig, (ax1, ax2) = plt.subplots(1, 2)
        # fig.set_size_inches(18, 7)
        # ax1.set_xlim([-0.1, 1])
        # The (n_clusters+1)*10 is for inserting blank space between silhouette
        # plots of individual clusters, to demarcate them clearly.
        # ax1.set_ylim([0, len(data) + (n_clusters + 1) * 10])

        clusterer = KMeans(n_clusters=n_clusters, random_state=10)
        cluster_labels = clusterer.fit_predict(data)

        silhouette_avg = silhouette_score(data, cluster_labels)
        print("For n_clusters =", n_clusters,
              "The average silhouette_score is :", silhouette_avg)

        # Compute the silhouette scores for each sample
        sample_silhouette_values = silhouette_samples(data, cluster_labels)


def kmeans_clustering(data: pd.DataFrame, clusters: int = 2):
    k_means = KMeans(n_clusters=clusters, n_init=10)
    k_means.fit(data)
