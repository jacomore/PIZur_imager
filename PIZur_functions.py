from pipython import GCSDevice,pitools, GCS2Commands
import zhinst.utils
import numpy as np

def process_raw_data(signal_paths,raw_data,index):
    """Gets and process raw_rata and updates data value

    Parameters
    ----------
    signal_paths : list
        list of strings of the subscribed nodes
    raw_data : dict
        dictionary in which read data are stored
    print_cols : index
        index : int
        number that contains the number of step of the scan so far

    Returns
    -------
    _ : float
        value that contains the average over the columns
    """
    for i, signal_path in enumerate(signal_paths):
        for signal_burst in raw_data.get(signal_path.lower(),[]):
            # skip the first two steps (required for calibration)
            if index >= 2:
                value = signal_burst["value"][index-2,:]
                return np.mean(value)

def input_new_scan_edges(old_edges, axis_edges):
    """Asks for and returns new edges for the 1D scan
    
    Parameters
    ----------
    old_edges : list 
        Two float elements with the input edges of the scan
    axis_edges : list
        Two float elements with the physical edges of the axes

    Returns
    -------
    None 
    """ 

    print(f"Invalid input: desired scan range [{old_edges[0]},{old_edges[1]}] is not within axis range: [{axis_edges[0]},{axis_edges[1]}]")
    while True: 
        try:
            neg = float(input("Please, type a new value for the negative edge: "))
            pos = float(input("Please, type a new value for the positive edge: "))
            break
        except ValueError:
            print("That was no valid number!")
    new_edges = [neg,pos]
    return new_edges

def target_within_axis_edges(scan_edges,axis_edges):
    """
    Sorts values of scan_edges and, is they are not comprised in axis_edges,
    invokes input_new_edges to get new edges


    Parameters
    ----------
    scan_edges : list 
        Two float elements with the input edges of the scan
    axis_edges : list
        Two float elements with the physical edges of the axes

    Returns
    -------
    scan_edges : list
        Two float elements with the input edges of the scan, either modified
        or unchanged if they are not within the axis_edges.
    """ 

    scan_edges.sort()
    if (scan_edges[0] < axis_edges[0] or scan_edges[1] > axis_edges[1]):
        scan_edges = input_new_scan_edges(scan_edges,axis_edges) 
        target_within_axis_edges(scan_edges,axis_edges)
    return scan_edges

def onedim_partition(scan_edges,stepsize,direction):
    """ returns the partition of the target points for a 1D scan    
    
    Parameters
    ----------
    scan_edges : list 
        Two float elements with the input edges of the scan
    stepsize : list
        A float with the size of the step of the 1D scan
    direction: str
        defines the direction of motion (FRWD = forward, BRWD = backward)

    Returns
    -------
    targets : numpy.array
        one-dimensional numpy array with the target points of the scan
    """ 

    Npoints = int((scan_edges[1]-scan_edges[0])/stepsize) + 1
    if direction == "FRWD":
        targets = np.linspace(scan_edges[0],scan_edges[1],Npoints,endpoint=  True)
    elif direction == "BCWD":
        targets = np.linspace(scan_edges[1],scan_edges[0],Npoints,endpoint=  True)
    return targets

