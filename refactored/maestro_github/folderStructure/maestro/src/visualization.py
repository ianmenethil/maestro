import matplotlib.pyplot as plt
import numpy as np

def plot_results(data, labels=None):
    """Plots the results of the data analysis.

    Args:
        data (list or numpy.ndarray): The data points to visualize.  Should be a list of lists or a numpy array.
        labels (list, optional):  Labels for the data points. Defaults to None.

    Returns:
        None
    """
    if isinstance(data,list):
        data = np.array(data)
    if data.ndim == 1:
        plt.plot(data)
    else:
        plt.plot(data.T) # Transpose for multiple lines
    if labels:
        plt.legend(labels)
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.title("Data Visualization")
    plt.show()
