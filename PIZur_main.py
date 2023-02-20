from PI_commands import *
from Zhinst_commands import zhinst_lockin
from PIZur_functions import *
import numpy as np
import json
import os
from datetime import datetime

# input parameters
f = open('input_dicts.json')
PIZur_inputs = json.load(f)
pi = PIZur_inputs["pi"]
zurich = PIZur_inputs["zurich"]
input_sig_pars = PIZur_inputs["input_signal_pars"]
demod_pars = PIZur_inputs["demod_pars"]
osc_pars = PIZur_inputs["oscillator_pars"]
data_acquisition_pars = PIZur_inputs["data_acquisition_pars"]

### Data acquisition parameters
burst_duration = data_acquisition_pars["duration"]
num_cols = int(np.ceil(demod_pars["rate"]* burst_duration))  
num_rows = int((pi["scan_edges"][1]-pi["scan_edges"][0])/pi["stepsize"] - 1)  
triggernode = "/%s/demods/%d/sample.TrigIn1" % (zurich["device_id"],demod_pars["trigger_demod_index"])
dir_to_save = os.getcwd()+"\\"+"Results"

further_data_acquisition_pars = {
                    			"type" : 6,
			                    "edge" : 2, 
			                    "duration" : burst_duration,
			                    "delay" : 0,
			                    "holdoff/time" : burst_duration,
			                    "holdoff/count" : 0,
			                    "triggernode" : triggernode,
			                    "grid/cols" : num_cols,
			                    "grid/rows" : num_rows,
			                    "save/directory": dir_to_save
                                }

data_acquisition_pars = {**data_acquisition_pars, **further_data_acquisition_pars}

# 0) Setup one controller: switch servo-on and reference
# ----------------------------------------------------------
onedev = Stepper(pi["ID"],pi["stage_ID"])
onedev.connect_pidevice()
onedev.move_stage_to_ref(pi["refmode"])
onedev.configure_out_trig(type = 6)

"""
# 1) Setup the controllers: switch servo-on and reference
# ----------------------------------------------------------
twodev = StepperChain(pi['ID'],pi['stage_ID'])
twodev.connect_daisy([1,2])
twodev.reference_both_stages([pi["refmode"],pi["refmode"]])
"""

# 2) Setup the zhinst and the data acquisition tab
# ----------------------------------------------------------
lock_in = zhinst_lockin(zurich)
lock_in.input_signal_settings(input_sig_pars)
lock_in.demod_signal_settings(demod_pars)
lock_in.oscillator_setting(osc_pars)
# data acquisition setup
lock_in.data_acquisition_setting(data_acquisition_pars)
# subscribe to signals: average of module and phase of the demodulated signal
demod_path = f"/{zurich['device_id']}/demods/{demod_pars['trigger_demod_index']}/sample"
signal_paths = []
signal_paths.append(demod_path + ".R.avg") 
signal_paths.append(demod_path + ".Theta.avg")  
signal_paths.append(data_acquisition_pars["triggernode"])  
lock_in.subscribe_to_signals(signal_paths)

# 3) Setup 1D analysis
# ----------------------------------------------------------
# define target positions through numpy linspace
targets = onedim_partition(pi["scan_edges"],pi["stepsize"],pi["motion_direction"])
# initialise an array with actual position that are reached by the controller
positions = np.empty(len(targets),dtype = np.float16)
# create instance of the pidevice
dev1D = onedev.pidevice
# create instance of the daq_module for 1D scan
daq1D = lock_in.daq_module
# starts module execution
daq1D.execute()

for index , position in enumerate(targets):  
    if not daq1D.finished():
        start = datetime.now()
        raw_data = daq1D.read(True)
        # read the data as soon as the trigger is detected
        # move axis toward point of partition
        dev1D.MOV(dev1D.axes,position)
        # wait until axes are on target
        intermediate = datetime.now()
        pitools.waitontarget(dev1D)
        end = datetime.now()
        # store actual position onto positions
        positions[index] = dev1D.qPOS(dev1D.axes)['1']
        print("Target:",targets[index],"Position:",positions[index])
    else: 
        raw_data = daq1D.read(True)
        print("Acquisition finished!")
 