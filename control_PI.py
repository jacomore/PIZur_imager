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

def line_scan_partition(scan_edges,stepsize):
    """ return the partition over which the axis will move"""
    #number of points of the partition
    Npoints = int((scan_edges[1]-scan_edges[0])/stepsize) + 1
    # define target positions through numpy linspace
    targets = np.linspace(scan_edges[0],scan_edges[1],Npoints,endpoint=  True)
    # assert that the last target point is smaller than the positive scan edge
    assert(targets[-1] <= scan_edges[1])
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

CONTROLLERNAME = 'C-663'
STAGES = 'L-406.40SD00'  # connect stages to axes
#REFMODES = 'FPL'
REFMODES = 'FNL'
scan_edges = [0,10]
stepsize = 1

with GCSDevice(devname = CONTROLLERNAME) as pidevice: 
    # return list of string with the found devices
    devices = pidevice.EnumerateUSB(mask=CONTROLLERNAME)
    # check that devices is not empty        
    if not devices: 
       raise Exception("There are no connected devices! Please, connect at least one device.")

    # printout found devices
    for i, device in enumerate(devices):
        print('Number ---- Device')
        print('{}      ----  {}'.format(i,device))

    # read the selected device
    item = int(input('Input the index of the device to connect:'))
    pidevice.ConnectUSB(devices[item])
    print('connected: {}'.format(pidevice.qIDN().strip()))

    # initialise the controller and the stages
    pitools.startup(pidevice, stages = STAGES, refmodes = REFMODES)
    
    # move towards REFMODE and wait until stage is ready on target
    move_to_ref(pidevice,REFMODES)
    
    # return values of the minimum and maximum position of the travel range of axis
    rangemin = list(pidevice.qTMN().values())
    rangemax = list(pidevice.qTMX().values())
    ranges = zip(rangemin,rangemax)
    
    for min,max in ranges:
        # check whether scan edges are within allowed range and sort scan_edges values
        scan_edges = target_within_range(scan_edges,[min,max])
    
    # define target positions through numpy linspace
    targets = line_scan_partition(scan_edges,stepsize)
    
    # execute the line scan and return the sampled positions
    positions = line_scan_execution(pidevice,targets)
