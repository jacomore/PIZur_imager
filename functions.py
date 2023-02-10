from pipython import GCSDevice,pitools, GCS2Commands
import zhinst.utils
import numpy as np

def move_stage_to_ref(pidevice,refmode):
    """Moves the stage towards the selected reference point

    Parameters
    ----------
    pidevice : GCSDevice object
        instance of the PI device
    refmode : str
        string that defines the reference point (FNL = negative, FPL = positive)

    Returns
    -------
    None 
    """    
    
    if refmode == 'FNL':
        pidevice.FNL()
    elif refmode == 'FPL':
        pidevice.FPL()
    pitools.waitontarget(pidevice)
    print("Stage: {}".format(GCS2Commands.qCST(pidevice.axes)),"successfully referenced")

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

def scan1D_partition(scan_edges,stepsize,direction):
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

def line_scan_execution(pidevice,targets):
    """ Perform the 1D line scan and returns the array 'positions' 
        that contains the positions over which the stages has stopped."""
    # empty vector to find the actual position of the stepper
    positions = np.empty(len(targets),dtype = np.float16)
    for index,pos in enumerate(targets): 
        # move axis toward point of partition
        pidevice.MOV(pidevice.axes,pos)
        # wait until axes are on target
        pitools.waitontarget(pidevice)
        # store actual position onto positions
        positions[index] = pidevice.qPOS(pidevice.axes)['1']
        print("Target:",targets[index],"Position:",positions[index])
    return positions

def configure_out_trig(pidevice,axis,type):
    """
    Configures and sets the output trigger for a given axis

    Parameters
    ----------
    pidevice: PIDevice object
        instance of the PI device
    axis: int
        number that identifies the axis whose trigger must be output
    type: int
        type of trigger to be output (6 ==  in Motion, 1 = Line trigger)

    Returns
    -------
    None
    """

    GCS2Commands.CTO(pidevice,1,2,axis)
    GCS2Commands.CTO(pidevice,1,3,type)
    # enable trigger output with the configuration defined above
    GCS2Commands.TRO(pidevice,1,True)
    return

def axis_edges(pidevice):
    """ evaluate and return the allowed range for the given axis. In particular, 
    it calculates the edges of axis. 

    Parameters
    ----------
    pidevice: PIDevice object
        instance of the PI device


    Returns
    -------
    ranges : zip object --> zip object that contains th edges of the single axis as a tuple
    """
    
    rangemin = list(pidevice.qTMN().values())
    rangemax = list(pidevice.qTMX().values())
    ranges = zip(rangemin,rangemax)
    return ranges