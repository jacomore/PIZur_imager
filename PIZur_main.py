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

# 1) Setup the controller: switch servo-on and reference
# ----------------------------------------------------------
pidevice = GCSDevice(devname = controller_name)
devices = pidevice.EnumerateUSB(mask=controller_name)
# check that at least one device is connected        
if not devices: 
    raise Exception("There are no connected devices! Please, connect at least one device.")
# print out connected devices
for i, device in enumerate(devices):
    print('Number ---- Device')
    print('{}      ----  {}'.format(i,device))
# I/O for device selection
item = int(input('Input the index of the device to connect:'))
pidevice.ConnectUSB(devices[item])
print('connected: {}'.format(pidevice.qIDN().strip()))    
# initialise the controller and the stages
pitools.startup(pidevice, stages = stage, refmodes = refmode)
# move towards refmode and wait until stage is ready on target
move_stage_to_ref(pidevice,refmode)
# set trigger output to "In motion"
configure_out_trig(pidevice,axis = 1,type = 6)
# return values of the minimum and maximum position of the travel range of axis
ranges = axis_edges(pidevice)

for min_val,max_val in ranges:
    # check whether scan edges are within allowed range and sort scan_edges values
    scan_edges = target_within_axis_edges(scan_edges,[min_val,max_val])
# ----------------------------------------------------------

# 2) Setup the zhinst and the data acquisition tab
# ----------------------------------------------------------
daq, device, props = zhinst.utils.create_api_session(device_id,
                                                    apilevel_example, 
                                                    server_host=server_host,
                                                    server_port=server_port)

# setting debugging level (the higher the value, the lower the verbosity)
daq.setDebugLevel(3)
# create an initial condition in which everything is deactivated (tabula rasa)
zhinst.utils.disable_everything(daq, device)
# calculate time constant 
timeconstant = zhinst.utils.bw2tc(demod_bandwidth, demod_order) 
exp_setting = [
    ["/%s/sigins/%d/ac" % (device_id, in_channel), ac_filter],                                            # AC filter
    ["/%s/sigins/%d/imp50" % (device_id, in_channel), imp50],                                         # match 50 Ohm impedance
   # ["/%s/sigins/%d/autorange" % (device_id, in_channel),1], # range of the input voltage (sensitivity)
    ["/%s/sigins/%d/range" % (device_id, in_channel),amplitude], # range of the input voltage (sensitivity)
    ["/%s/demods/%d/enable" % (device_id, trigger_demod_index), 1],                               # switch on demodulator (?)
    ["/%s/demods/%d/rate" % (device_id, trigger_demod_index), demod_rate],                             
    #["/%s/demods/%d/adcselect" % (device_id, trigger_demod_index), in_channel],                   # selector of the signal to be converted into digital 
    ["/%s/demods/%d/order" % (device_id, trigger_demod_index), demod_order],                      
    ["/%s/demods/%d/timeconstant" % (device_id, trigger_demod_index), timeconstant],
    ["/%s/demods/%d/oscselect" % (device_id, trigger_demod_index), osc_index],                    
    ["/%s/demods/%d/harmonic" % (device_id, trigger_demod_index), harmonic],
    ["/%s/oscs/%d/freq" % (device_id, osc_index), frequency],
              ]
# upload above defined settings
daq.set(exp_setting)
# Wait for the demodulator filter to settle.
timeconstant_set = daq.getDouble(
    "/%s/demods/%d/timeconstant" % (device, trigger_demod_index)
    )
time.sleep(10 * timeconstant_set)
# perform a global synchronisation between the device and the data server")
daq.sync()
# Create an instance of the data acquisition module.
daq_module = daq.dataAcquisitionModule()
# set length of the history acquisition
daq_module.set('historylength', 100000) # length of the history acquisition

# Set the device that will be used for the trigger
daq_module.set("device", device_id)
# trigger mode 6 --> hardware trigger
daq_module.set("type", 6)
# set the triggernode to the Digital Trigger Port 1 in the back panel
triggerpath = '/dev4910/demods/0/sample.TrigIn1'
triggernode = triggerpath
daq_module.set("triggernode", triggernode)
# trigger on the negative edge
daq_module.set("edge", 2)
# no trigger delay
trigger_delay = 0
daq_module.set("delay", trigger_delay)
# Do not return overlapped trigger events -->  set an hold-off time of 50 ms
hold_off_time = 0.05
daq_module.set("holdoff/time", hold_off_time)
daq_module.set("holdoff/count", 0)
# setting grid mode "exact (on grid)"
daq_module.set("grid/mode", 4) 
#  Do not perform average (only 1 acquisition)
daq_module.set("grid/repetitions", 1)
# number of bursts and cols
burst_duration = 0.05 # 50 ms
num_cols = int(np.ceil(demod_rate* burst_duration))  
# set the number of cols in the grid
daq_module.set("grid/cols", num_cols)
# set the number of rows in the grid
num_rows = int((np.floor(scan_edges[1]-scan_edges[0])/stepsize + 1))
daq_module.set("grid/rows", num_rows)
# direction of data saving
daq_module.set('save/directory', 'C:\\Users\\ophadmin\\Desktop\\PIZur_imager\\Test1')
# set endless mode to false
daq_module.set("endless",0)
# saving filename
filename = "DAQ_1Dscan_test1"
daq_module.set("save/fileformat", "csv")
daq_module.set("save/filename", filename)
# 'save/saveonread' - save the data each time read() is called.
daq_module.set("save/saveonread", True)
# subscribe to signals: average of module and phase of the demodulated signal
demod_path = f"/{device_id}/demods/0/sample"
signal_paths = []
signal_paths.append(demod_path + ".R.avg") 
signal_paths.append(demod_path + ".Theta.avg")  
data = {}
for signal_path in signal_paths:
    print("Subscribing to ", signal_path)
    daq_module.subscribe(signal_path)
    data[signal_path] = []

# 3) 1D execution and data acquisition
# ----------------------------------------------------------
# define target positions through numpy linspace
targets = scan1D_partition(scan_edges,stepsize,direction)
# initialise an array with actual position that are reached by the controller
positions = np.empty(len(targets),dtype = np.float16)
# starts module execution
daq_module.execute()

while not daq_module.finished():
    for index , position in enumerate(targets):  
        # read the data as soon as the trigger is detected
        raw_data = daq_module.read(True)
        # move axis toward point of partition
        pidevice.MOV(pidevice.axes,position)
        # wait until axes are on target
        pitools.waitontarget(pidevice)
        # store actual position onto positions
        positions[index] = pidevice.qPOS(pidevice.axes)['1']
        print("Target:",targets[index],"Position:",positions[index])
        process_raw_data(raw_data,index)