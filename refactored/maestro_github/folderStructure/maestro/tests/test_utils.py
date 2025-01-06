import unittest
from utils import calculate_data, load_data
import numpy as np
import os
import tempfile

class TestUtils(unittest.TestCase):
    def test_calculate_data(self):
        self.assertEqual(calculate_data([1, 2, 3]), [2, 4, 6])
        self.assertEqual(calculate_data([]), [])

    def test_load_data_valid(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            np.savetxt(temp_file, [1, 2, 3])
            temp_filepath = temp_file.name
        data = load_data(temp_filepath)
        self.assertTrue(np.array_equal(data, np.array([1, 2, 3])))
        os.remove(temp_filepath)


    def test_load_data_invalid_file(self):
        self.assertIsNone(load_data("nonexistent_file.txt"))

    def test_load_data_invalid_format(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("This is not a valid numpy file")
            temp_filepath = temp_file.name
        self.assertIsNone(load_data(temp_filepath))
        os.remove(temp_filepath)

if __name__ == '__main__':
    unittest.main()