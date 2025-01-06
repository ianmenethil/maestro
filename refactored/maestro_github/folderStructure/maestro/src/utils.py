import numpy as np

def calculate_data(input_data):
    """
    Calculates processed data from input data.

    Args:
        input_data (list): A list of input values to be processed.

    Returns:
        list: A list of calculated results.
    """
    #Example Calculation
    return [x * 2 for x in input_data]

def load_data(filepath):
    """Loads data from a specified filepath.

    Args:
        filepath (str): The path to the data file.

    Returns:
        numpy.ndarray: The loaded data as a NumPy array.
        Returns None if there is an error.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file format is invalid.
    """
    try:
        data = np.loadtxt(filepath)
        return data
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None
    except ValueError:
        print(f"Error: Invalid file format at {filepath}")
        return None
