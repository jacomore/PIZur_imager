from PI_commands import *
from Zhinst_commands import zhinst_lockin
import numpy as np

### PI:
scan_edges = [0,11]
stepsize = 0.1
num_grids = 1

pi = {'ID':'C-663',
              'stage_ID': 'L-406.40SD00',
              'refmode': 'FNL',
              'motion_direction':'FRWD'}

zurich = { 'device_id':'dev4910',
                'server_host':'169.254.196.174',
                'apilevel' : 6,
                'server_port' : 8004
                }

### Zurich:
### Zurich params
in_channel = 0          # Input channel V1
trigger_demod_index = 0 # demodulator 1
osc_freq = 100         # frequency of the internal oscillator
osc_index = 0

input_signal_pars = {
                     'ac' : 0, 
                     'imp50' : 0,
                     'range': 1.0,
                    }

demod_pars = {'enable' : 1,
              'rate' : 10e3,
              'adcselect' : trigger_demod_index,
              'order' : 3,
              'oscselect' : osc_index,
              'harmonic' : 1,
              'bandwidth' : 10
             }

### Data acquisition parameters
burst_duration = 0.05 # 50 ms
num_cols = int(np.ceil(demod_pars["rate"]* burst_duration))  
num_rows = int((scan_edges[1]-scan_edges[0])/stepsize - 1)  
filename = "test"

data_acquisition_pars = { 'historyLength' : 100000,
                          'device': zurich["device_id"],
                          'type' : 6,
                          'triggernode' : '/dev4910/demods/0/sample.TrigIn1',
                          'edge' : 2, 
                          'duration' : 0.05,
                          'delay' : 0,
                          'holdoff/time' : 0.05,
                          'holdoff/count' : 0,
                          'grid/mode' : 4,
                          'grid/repetitions':1,
                          'grid/cols' : num_cols,
                          'grid/rows' : num_rows,
                          'save/directory': 'C:\\Users\\ophadmin\\Desktop\\PIZur_imager\\PIZur_imager\\Test',
                          'endless' : 0,
                          'save/filename': filename,
                          'save/fileformat': 'csv',
                          'save/saveonread' : True,
                        }

# 1) Setup the controller: switch servo-on and reference
# ----------------------------------------------------------
twodev = StepperChain(pi['ID'],pi['stage_ID'])
twodev.connect_daisy([1,2])
twodev.reference_both_stages(["FNL","FNL"])"

# 2) Setup the zhinst and the data acquisition tab
# ----------------------------------------------------------
lock_in = zhinst_lockin(zurich)
lock_in.input_signal_settings(in_channel,input_signal_pars)
lock_in.demod_signal_settings(trigger_demod_index,demod_pars)
lock_in.oscillator_setting(osc_index,osc_freq)
# data acquisition setup
lock_in.data_acquisition_setting(data_acquisition_pars)
# subscribe to signals: average of module and phase of the demodulated signal
demod_path = f"/{zurich['device_id']}/demods/{trigger_demod_index}/sample"
signal_paths = []
signal_paths.append(demod_path + ".R.avg") 
signal_paths.append(demod_path + ".Theta.avg")  
signal_paths.append(data_acquisition_pars["triggernode"])  
lock_in.subscribe_to_signals(signal_paths)

"""
# 3) 1D execution and data acquisition
# ----------------------------------------------------------
# define target positions through numpy linspace
targets = scan1D_partition(scan_edges,stepsize,controller["motion_direction"])
# initialise an array with actual position that are reached by the controller
positions = np.empty(len(targets),dtype = np.float16)
# starts module execution
daq_module.execute()

for index , position in enumerate(targets):  
    if not daq_module.finished():
        raw_data = daq_module.read(True)
        print(daq_module.progress())
        # read the data as soon as the trigger is detected
        # move axis toward point of partition
        pidevice.MOV(pidevice.axes,position)
        # wait until axes are on target
        pitools.waitontarget(pidevice)
        # store actual position onto positions
        positions[index] = pidevice.qPOS(pidevice.axes)['1']
        print("Target:",targets[index],"Position:",positions[index])
        data = process_raw_data(signal_paths, raw_data,index)
    else: 
        raw_data = daq_module.read(True)
        print(raw_data)
        print("Acquisition finished!")
 
"""

    
