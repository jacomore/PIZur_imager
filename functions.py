
from pipython import GCSDevice,pitools, GCS2Commands
import numpy as np 

def move_to_ref(pidevice,REFMODES):
    """move the stage towards the reference point"""
    if REFMODES == 'FNL':
        pidevice.FNL()
    elif REFMODES == 'FPL':
        pidevice.FPL()
    pitools.waitontarget(pidevice)
    print("Stage: {}".format(GCS2Commands.qCST(pidevice)['1']),"successfully referenced")

def input_new_edges(old_edges, axis_edges):
    """ 
        IO_newinput is called when the input range for 1D scan is not comprised in the allowed range.
        New inputs are thus required and the new_edges are returned
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

def target_within_range(scan_edges,axis_edges):
    """
    target_within_range sort values of scan_edges. Then, if scan_edges is not fully comprised in axis_edges, 
    input_new_edges is invoked to get new edges. Eventually, target_within_range is called recursively to 
    check that the new input satisfy the condition. 
    """
    scan_edges.sort()
    if (scan_edges[0] < axis_edges[0] or scan_edges[1] > axis_edges[1]):
        scan_edges = input_new_edges(scan_edges,axis_edges) 
        target_within_range(scan_edges,axis_edges)
    return scan_edges

def line_scan_partition(scan_edges,stepsize,DIRECTION):
    """ return the partition over which the axis will move"""
    #number of points of the partition
    Npoints = int((scan_edges[1]-scan_edges[0])/stepsize) + 1
    # define target positions through numpy linspace
    if DIRECTION == "FRWD":
        targets = np.linspace(scan_edges[0],scan_edges[1],Npoints,endpoint=  True)
    elif DIRECTION == "BCWD":
        targets = np.linspace(scan_edges[1],scan_edges[0],Npoints,endpoint=  True)
    # assert that the last target point is smaller than the positive scan edge
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
    return positions

def trigger_config(pidevice,axis,type):
    """
    set output trigger type for a given axis and enable it. 
    ----------
    pidevice: input --> instance of PIDevice class
    axis: integer --> axis whose trigger must be output
    type: integer --> type of trigger; 6 ==  in Motion
                                       1 = Line trigger...
    """
    # set trigger output to "In motion"
    GCS2Commands.CTO(pidevice,1,2,axis)
    GCS2Commands.CTO(pidevice,1,3,type)
    # enable trigger output with the configuration defined above
    GCS2Commands.TRO(pidevice,1,True)
    return

def axis_edges(pidevice):
    """
    evaluate and return the allowed range for the given axis. In particular, 
    it calculates the edges of axis. 
    ----------------
    pidevice: input --> instance of PIDevice class
    ranges : output --> zip object that contains th edges of the single axis as a tuple
    """
    rangemin = list(pidevice.qTMN().values())
    rangemax = list(pidevice.qTMX().values())
    ranges = zip(rangemin,rangemax)
    return ranges