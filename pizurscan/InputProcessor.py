import numpy as np

def rows_columns_contiuous(delta, stepsize):
    """
    Calculate the number of rows and columns for a continuous scan with a PI controller and Zurich lock-in.

    Parameters:
    -----------
    delta : float
        The distance between the scan edges.
    stepsize : float
        The step size for the motion of the stepper.

    Returns:
    --------
    N_rows : int
        The number of rows for the data acquisition.
    N_cols : int
        The number of columns for the data acquisition.
    """
    N_rows = 1
    N_cols = int(np.floor(delta / stepsize)) + 1
    return N_rows, N_cols

def rows_columns_discrete(delta, stepsize, sampl_freq):
    """
    Calculate the number of rows and columns for a discrete scan with a PI controller and Zurich lock-in.
    
    Parameters:
    -----------
    delta : float
        The distance between the scan edges.
    stepsize : float
        The step size for the motion of the stepper.
    sampl_freq : float
        The sampling frequency of the Zurich lock-in.

    Returns:
    --------
    N_rows : int
        The number of rows for the data acquisition.
    N_cols : int
        The number of columns for the data acquisition.
    """
    N_rows = int(np.floor(delta / stepsize)) + 1
    N_cols = int(np.floor(0.05 * sampl_freq))
    return N_rows, N_cols

def evaluate_daq_pars(scan_pars):
    """
    Process input data for a 1D scan to return the complete DAQ parameters that suit the scan parameters.

    Parameters:
    -----------
    scan_pars : dict
        A dictionary containing scan parameters, including:
            - stepsize : float
                The step size for motin of the stepper
            - acceleration : float
                The acceleration of the stepper.
            - velocity : float
                The velocity of the stepper.
            - sampling_freq : float
                The sampling frequency of the Zurich lock-in
            - type : str
                The type of scan: 'continuous' or 'discrete'.
            - scan_edges : list[float]
                The edges of the scan range.

    Returns:
    --------
    daq_pars : dict
        A dictionary containing data acquisition parameters, including:
            - daq_columns : int
                The number of columns for the data acquisition.
            - daq_rows : int
                The number of rows for the data acquisition.
            - duration : float
                The duration of the triggered data acquisition.
            - mode : str
                The data acquisition mode; 'Linear' for continuous scan, 'Exact (on-grid)' for discrete scan.
            - trigger_type : str
                The trigger type, always set to 'HW trigger'.
            - trigger_edge : str
                The trigger edge.
            - holdoff : float
                The holdoff time for the trigger.
    """
    stepsize = scan_pars["stepsize"]
    acc = scan_pars["acceleration"]
    vel = scan_pars["velocity"]
    sampl_freq = scan_pars["sampling_freq"]
    scan_type = scan_pars["type"]
    scan_edges = scan_pars["scan_edges"]

    delta = delta_calculator(scan_edges)

    if scan_type == "continuous":
        duration = duration_calculator(delta, vel, acc)
        N_rows, N_cols = rows_columns_contiuous(delta, stepsize)
        mode = "Linear"
        edge = "positive"
    else:
        duration = 0.05  # 50 milliseconds
        N_rows, N_cols = rows_columns_discrete(delta, stepsize, sampl_freq)
        mode = "Exact (on-grid)"
        edge = "negative"

    daq_pars = {
        "daq_columns": N_cols,
        "daq_rows": N_rows,
        "duration": duration,
        "mode": mode,
        "trigger_type": "HW trigger",
        "trigger_edge": edge,
        "holdoff": duration * 0.95,
    }
    return daq_pars

def delta_calculator(scan_edges):
    """
    Calculate the absolute value of the distance between the scan edges.

    Parameters:
    -----------
    scan_edges : list[float]
        The edges of the scan range.

    Returns:
    --------
    delta : float
        Absolute value of the distance between scan edges.
    """
    return abs(scan_edges[1] - scan_edges[0])

def duration_calculator(delta, vel, acc):
    """
    Calculate the duration of the triggered data acquisition for a continuous scan.

    Parameters:
    -----------
    delta : float
        The distance between the scan edges.
    vel : float
        The velocity of the stepper.
    acc : float
        The acceleration of the stepper.

    Returns:
    --------
    duration : float
        The duration of the triggered data acquisition.
    """
    if np.sqrt(acc * delta) > vel:
        duration = vel / acc + delta / vel
    else:
        duration = 2 * np.sqrt(delta / acc)
    return duration