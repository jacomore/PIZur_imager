from pipython import GCSDevice,pitools, GCS2Commands
from . import functions as fc
#import logging
#logging.basicConfig(level=logging.DEBUG)

CONTROLLERNAME = 'C-663'
STAGES = 'L-406.40SD00'  # connect stages to axes
#REFMODES = 'FPL'
REFMODES = 'FNL'
scan_edges = [0,10]
stepsize = 1
#DIRECTION = "FRWD"
DIRECTION = "BCWD"


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
    fc.move_to_ref(pidevice,REFMODES)
    # set trigger output to "In motion"
    fc.trigger_config(pidevice,axis = 1,type = 6)
    
    # return values of the minimum and maximum position of the travel range of axis
    ranges = fc.axis_edges(pidevice)
    
    for min,max in ranges:
        # check whether scan edges are within allowed range and sort scan_edges values
        scan_edges = fc.target_within_range(scan_edges,[min,max])
    
    # define target positions through numpy linspace
    targets = fc.line_scan_partition(scan_edges,stepsize,DIRECTION)
    
    # execute the line scan and return the sampled positions
    positions = fc.line_scan_execution(pidevice,targets)
