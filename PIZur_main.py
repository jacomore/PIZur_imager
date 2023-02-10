from pipython import GCSDevice,pitools, GCS2Commands
import zhinst.utils
from PIZur_functions import *
import time
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------
### PI PARAMETERS:
controller_name = 'C-663'
stage = 'L-406.40SD00'  # connect stage to axes
#refmode = 'FPL'
refmode = 'FNL'
#direction = "FRWD"
direction = "BCWD"

### Scan:
scan_edges = [0,11]
stepsize = 0.1
# ---------------------------------------------------------

# ---------------------------------------------------------
# ZHINST PARAMETERS:
device_id = 'dev4910'
num_grids = 1
server_host = "169.254.196.174"
apilevel_example = 6  
server_port =8004

### Demodulator:
in_channel = 0          # Input channel V1
amplitude = 1.0         # sensitivity of the lock-in
trigger_demod_index = 0 # demodulator 1
osc_index = 0           # oscillator of demodulator 1 (manual !!)
demod_rate = 10e3       # demodulator sampling rate: 100 kHz
demod_order = 4         # filtering order of the demulator
demod_bandwidth = 10    # bandwidth of the demodulator
frequency = 100         # frequency of the internal oscillator
ac_filter = 0           # AC Filter; 1 = activated, 0 = deactivated
imp50 = 0               # set 50 Ohm impedance at the entrace; 1 = activated, 0 = deactivated
harmonic = 1            # set multiple of the oscillator frequency for demulating
# ---------------------------------------------------------

with GCSDevice(devname = controller_name) as pidevice: 
    # return list of string with the found devices
    devices = pidevice.EnumerateUSB(mask=controller_name)
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

    # initialise the controller and the stage
    pitools.startup(pidevice, stage = stage, refmode = refmode)
    # move towards REFMODE and wait until stage is ready on target
    move_stage_to_ref(pidevice,refmode)
    # set trigger output to "In motion"
    configure_out_trig(pidevice,axis = 1,type = 6)
    
    # return values of the minimum and maximum position of the travel range of axis
    ranges = axis_edges(pidevice)
    
    for min,max in ranges:
        # check whether scan edges are within allowed range and sort scan_edges values
        scan_edges = target_within_axis_edges(scan_edges,[min,max])
    
    # define target positions through numpy linspace
    targets = scan1D_partition(scan_edges,stepsize,direction)
    
    # execute the line scan and return the sampled positions
    positions = line_scan_execution(pidevice,targets)
