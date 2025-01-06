import unittest
from visualization import plot_results
import matplotlib
matplotlib.use('Agg') #For testing without a display
import matplotlib.pyplot as plt
import io
import numpy as np
import tempfile

class TestVisualization(unittest.TestCase):

    def test_plot_results_1d(self):
        data = [1,2,3,4,5]
        plot_results(data)

    def test_plot_results_2d(self):
        data = [[1,2],[3,4],[5,6]]
        plot_results(data)

    def test_plot_results_with_labels(self):
        data = [1,2,3]
        labels = ["A","B","C"]
        plot_results(data,labels)


if __name__ == '__main__':
    unittest.main()
