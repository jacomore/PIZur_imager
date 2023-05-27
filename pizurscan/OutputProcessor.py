import numpy as np

def get_raw_data(filename):
    """
    Read raw data from the input file and return the third column, which contains the values of the measured signal.

    Args:
    - filename (str): The name of the input file.

    Returns:
    - raw_data (ndarray): A NumPy array containing the third column of the input file.
    """
    raw_data = np.genfromtxt(filename, skip_header=1, delimiter=";")
    return raw_data[:, 2]

def evaluate_averaged_data(N_rows, N_cols, raw_data):
    """
    Average the input data in case of a 1D discrete scan. Raw data is divided into chunks of dimension N_cols, 
    over which an average is performed. The output avg_data is in one-to-one relation with the spatial coordinates.

    Args:
    - N_rows (int): The number of rows that was set in the daq.
    - N_cols (int): The number of columns that was set in the daq.
    - raw_data (ndarray): A NumPy array containing the raw data.

    Returns:
    - avg_data (ndarray): A NumPy array containing the averaged data.
    """
    avg_data = np.empty(N_rows)
    for row in range(N_rows):
        avg_data[row] = np.mean(raw_data[row * N_cols:(row + 1) * N_cols])
    return avg_data

def evaluate_target_positions(scan_edges, stepsize):
    """
    Evaluate the partition of the target points for a 1D scan.

    Args:
    - scan_edges (list): A list containing the scan range.
    - stepsize (float): The step size of the stepper.

    Returns:
    - targets (ndarray): A NumPy array containing the target positions.
    """
    # calculate target points
    N_points = int(abs(scan_edges[1] - scan_edges[0]) / stepsize) + 1
    return np.linspace(scan_edges[0], scan_edges[1], N_points, endpoint=True)

def save_data_file(targets, avg_data):         
    """
    Save the cleaned 1D data to a file named "cleaned_1D_data.txt" in output folder.

    Args:
    - targets (ndarray): A NumPy array containing the target positions.
    - avg_data (ndarray): A NumPy array containing the averaged data.
    """
    out_name = "output/cleaned_1D_data.txt"
    out_file = np.column_stack((targets, avg_data))
    np.savetxt(out_name, out_file, fmt="%10.6f", delimiter=",")

def save_processed_data(filename, scan_pars, daq_pars):
    """
    Process the 1D data, averaging it if necessary (discrete scan), and save it to 
    a file named "cleaned_1D_data.txt" that is stored in the "output" folder.

    Args:
    - filename (str): The name of the input file.
    - scan_pars (dict): A dictionary containing scan parameters.
    - daq_pars (dict): A dictionary containing data acquisition parameters.
    """
    # extract input values
    filename = "input/" + filename
    N_rows = daq_pars["daq_rows"]
    N_cols = daq_pars["daq_columns"]

    # get target positions
    scan_edges = scan_pars["scan_edges"]
    stepsize = scan_pars["stepsize"]
    targets = evaluate_target_positions(scan_edges, stepsize)  
    
    # get output data
    raw_data = get_raw_data(filename)
    if scan_pars["type"] == "discrete":
        out_data = evaluate_averaged_data(N_rows, N_cols, raw_data)
    else: 
        out_data = raw_data
    # save data
    save_data_file(targets, out_data)