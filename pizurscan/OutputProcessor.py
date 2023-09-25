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
    out_name = "../output/cleaned_data.txt"
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
    filename = "../output/" + filename
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
    
def evaluate_2D_targets(scan_pars):
    """
    Evaluate the target positions for a 2D scan.

    Args:
    - scan_pars (dict): A dictionary containing scan parameters.

    Returns:
    - targets (ndarray): A NumPy array containing the target positions for the primary axis.
    - servo_targets (ndarray): A NumPy array containing the target positions for the secondary axis.
    """
    targets = evaluate_target_positions(scan_pars["scan_edges"],scan_pars["stepsize"])
    servo_targets = evaluate_target_positions(scan_pars["servo_scan_edges"],scan_pars["servo_stepsize"])
    if scan_pars["main_axis"] == "master":
        return targets, servo_targets
    else:
        return servo_targets,targets

def save_2D_data_file(primary, secondary, out_data, N_rows, N_cols):
    """
    Save the cleaned 2D data to a file named "cleaned_2D_data.txt" in the current directory.

    Args:
    - primary (ndarray): A NumPy array containing the target positions for the primary axis.
    - secondary (ndarray): A NumPy array containing the target positions for the secondary axis.
    - out_data (ndarray): A NumPy array containing the cleaned data.
    - N_rows (int): The number of rows in the cleaned data.
    - N_cols (int): The number of columns in the cleaned data.
    """
    out_name = "..//output//cleaned_2D_data.txt"
    length_of_file = N_rows * N_cols
    out_file = np.empty((length_of_file,3))
    for row_idx,row in enumerate(secondary):
        row_file = np.empty(N_cols)
        row_file[:] = row
        out_file[row_idx*N_cols:(row_idx+1)*N_cols] =  np.column_stack((primary,row_file,out_data[row_idx*N_cols:(row_idx+1)*N_cols]))          
    np.savetxt(out_name, out_file, delimiter=",")

def save_processed_2D_data(filename, scan_pars, daq_pars):
    """
    Process the 2D data and save it to a file named "cleaned_2D_data.txt" in the current directory.

    Args:
    - filename (str): The name of the input file.
    - scan_pars (dict): A dictionary containing scan parameters.
    - daq_pars (dict): A dictionary containing data acquisition parameters.
    """
    targets1, targets2 = evaluate_2D_targets(scan_pars)
    ff = "..//output//"+str(filename)
    raw_data = get_raw_data(ff)
    if scan_pars["type"] == "discrete":
        out_data = evaluate_averaged_data(raw_data)
    else:
        out_data = raw_data
    save_2D_data_file(
        primary=targets1,
        secondary=targets2,
        out_data=out_data,
        N_rows=daq_pars["out_rows"],
        N_cols=daq_pars["out_columns"]
    )
