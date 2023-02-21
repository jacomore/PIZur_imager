import zhinst.utils
import time
import os
import numpy as np

class zhinst_lockin:
    """Setup output signals, oscillators, demodulators, and data acquisition tab of the 
        zhinst device.
   
    """
    def __init__(self,device_pars):
        self.device_id = device_pars["device_id"]
        self.daq, self.device, self.props = zhinst.utils.create_api_session(device_pars["device_id"],
                                                    device_pars["apilevel"], 
                                                    device_pars["server_host"],
                                                    device_pars["server_port"])
        self.daq.setDebugLevel(6)
        zhinst.utils.disable_everything(self.daq,self.device)
        
    def input_signal_settings(self,input_sig_pars):
        """upload on the lock-in all the settings for the input signal acquisition"""
        in_channel = input_sig_pars["input_channel"]
        for feature,value in input_sig_pars.items(): 
            if feature != "input_channel":
                self.daq.set("/%s/sigins/%d/%s"% (self.device_id,in_channel,feature),value)
        
    def demod_signal_settings(self,demod_pars):
        trigger_demod_index = demod_pars["trigger_demod_index"]
        """upload on the lock-in all the settings for the demodulators"""
        for feature,value in demod_pars.items():
            if feature not in ['bandwidth','trigger_demod_index'] :
                print(feature)
                self.daq.set("/%s/demods/%d/%s" % (self.device_id,trigger_demod_index,feature),value)

        timeconstant = zhinst.utils.bw2tc(demod_pars["bandwidth"], demod_pars["order"])
        self.daq.setDouble("/%s/demods/%d/%s" % (self.device_id,trigger_demod_index,"timeconstant"),timeconstant)
        # Wait for the demodulator filter to settle.
        timeconstant_set = self.daq.getDouble(
            "/%s/demods/%d/timeconstant" % (self.device, trigger_demod_index)
                                            )
        time.sleep(10 * timeconstant_set)
        # perform a global synchronisation between the device and the data server")
        self.daq.sync()
    
    def oscillator_settings(self,osc_pars):
        """ upload on the lock-in the setting for the oscillator channel"""
        self.daq.set("/%s/oscs/%d/freq" % (self.device_id, osc_pars["osc_index"]), osc_pars["osc_freq"])
            
    def join_data_acquisition_pars(self,data_acquisition_pars,demod_pars,PI):
        """Evaluate some parameters for the data acquisition that are deduced from the 
           other input parameters of the demodulator and of the scan."""
        burst_duration = data_acquisition_pars["duration"]
        num_cols = int(np.ceil(demod_pars["rate"]* burst_duration))  
        num_rows = int((PI["scan_edges"][1]-PI["scan_edges"][0])/PI["stepsize"] - 1)  
        triggernode = "/%s/demods/%d/sample.TrigIn1" % (self.zurich["device_id"],demod_pars["trigger_demod_index"])
        dir_to_save = os.getcwd()+"\\"+"Results"

        further_data_acquisition_pars = {
			                    "duration" : burst_duration,
			                    "holdoff/time" : burst_duration,
			                    "triggernode" : triggernode,
			                    "grid/cols" : num_cols,
			                    "grid/rows" : num_rows,
			                    "save/directory": dir_to_save
                                }
        return {**data_acquisition_pars, **further_data_acquisition_pars}

    def data_acquisition_settings(self,data_acquisition_pars):
        """upload on the lock-in all the settings for data acquisition"""
        self.daq_module = self.daq.dataAcquisitionModule()
        for feature,value in data_acquisition_pars.items():
            self.daq_module.set(feature,value)
    
    def subscribe_to_signals(self,signal_paths):
        self.data = {}
        for signal_path in signal_paths:
            print("Subscribing to ",signal_path)
            self.daq_module.subscribe(signal_path)
            self.data[signal_path] = []
    