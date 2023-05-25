import json
import sys

MAX_SPEED = 10  # mm/s
MIN_POS = 0     # mm
MAX_POS = 102   # mm
MIN_STEP = 5e-4 # mm
MAX_STEP = 102  # mm
MAX_ACC = 20    # mm/s^2

def input_validator():
    """
    Validates the scan parameters extracted from a JSON file and terminates the program if any validation error occurs.
    
    Returns:
        dict: A dictionary containing the input parameters for the scanning process.
    """
    scan_pars = extract_scan_pars()
    try:
        validate(scan_pars)
        return scan_pars
    except ValueError as e:
        print(e.args[0])
        print("Closing program ...")
        sys.exit()

def extract_scan_pars():
    """
    Extracts the scan parameters from a JSON file.

    Returns:
        dict: A dictionary containing the input parameters for the scanning process.
    """
    with open('../input/input_dicts.json') as openPars:
        inpars = json.load(openPars)
    scan_pars = inpars["scan_pars"]
    return scan_pars

def validate(scan_pars):
    """
    Validates all the input parameters of scan_pars.

    Args:
        scan_pars (dict): A dictionary containing the input parameters for the scanning process.

    Raises:
        ValueError: If any of the input parameters is invalid.
    """
    validate_type(scan_pars["type"])
    validate_scan_edges(scan_pars["scan_edges"])
    validate_stepsize(scan_pars["scan_edges"], scan_pars["stepsize"])
    validate_velocity(scan_pars["velocity"])
    validate_acceleration(scan_pars["acceleration"])
    
def validate_type(type):
    """
    Validates the type of the scanning process.

    Args:
        type (str): Type of the scan, either "continuous" or "discrete".

    Raises:
        ValueError: If the type is not "continuous" or "discrete".
    """
    if not (type == "continuous" or type == "discrete"):
        raise ValueError("Invalid input: type must be either continuous or discrete.")
    
def validate_scan_edges(scan_edges):
    """
    Validates the scan edges.

    Args:
        scan_edges (list): A list containing the starting and final points of the scan.

    Raises:
        ValueError: If the scan edges are out of range [0, 102].
    """
    if (scan_edges[0] < MIN_POS) or (scan_edges[0] > MAX_POS):
        raise ValueError("Invalid input: first scan edge is out of range [0,102].")
    if (scan_edges[1] < MIN_POS) or (scan_edges[1] > MAX_POS):
        raise ValueError("Invalid input: second scan edge is out of range [0,102].")
        
def validate_stepsize(scan_edges, stepsize):
    """
    Validates the step size of the scanning process.

    Args:
        scan_edges (list): A list containing the starting and final points of the scan.
        stepsize (float): The step size between scan points.

    Raises:
        ValueError: If the step size is out of range [0.0005, 102], or the starting point plus step size are
                    out of range.
    """
    if (stepsize < MIN_STEP) or (stepsize >= MAX_STEP):
        raise ValueError("Invalid input: step size is out of range [0.0005,102].")
    if scan_edges[0] < scan_edges[1]:
        if stepsize + scan_edges[0] > MAX_STEP:
            raise ValueError("Invalid input: first scan edge plus step size is out of range.")
    elif scan_edges[0] > scan_edges[1]:
        if scan_edges[0] - stepsize < MIN_STEP:
            raise ValueError("Invalid input: first scan edge minus step size is out of range.")
    else:
        raise ValueError("Invalid input: the scan edges coincide.")
        
def validate_velocity(velocity):
    """
    Validates the velocity attribute to ensure that it is within the range [0, 10] mm/s.

    Args:
        velocity (float): The velocity of the scan motion in mm/s.

    Raises:
        ValueError: If the velocity value is out of range [0, 10] mm/s.
    """
    if (velocity < 0) or (velocity > MAX_SPEED):
        raise ValueError("Invalid input: velocity value is out of range [0, 10] mm/s.")
        
def validate_acceleration(acceleration):
    """
    Validates the acceleration attribute to ensure that it is within the range [0, 20] mm/s^2.

    Args:
        acceleration (float): The acceleration of the scan motion in mm/s^2.

    Raises:
        ValueError: If the acceleration value is out of range [0, 20] mm/s^2.
    """
    if (acceleration < 0) or (acceleration > MAX_ACC):
        raise ValueError("Invalid input: acceleration value is out of range [0, 20] mm/s^2.")