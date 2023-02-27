import zhinst.utils
import time
import os
import numpy as np

class zhinst_lockin:
    """Set up output signals, oscillators, demodulators, and data acquisition tab of the 
        zhinst device.
    """
    def __init__(self, device_pars):
        """Initialize the zhinst_lockin class.

        Args:
            device_pars (dict): a dictionary containing the device parameters,
                including device_id, apilevel, server_host, and server_port.
        """
        self.device_id = device_pars["device_id"]
        self.daq, self.device, props = zhinst.utils.create_api_session(device_pars["device_id"],
                                                    device_pars["apilevel"], 
                                                    device_pars["server_host"],
                                                    device_pars["server_port"])
        self.daq.setDebugLevel(6)
        zhinst.utils.disable_everything(self.daq, self.device)
        
    def input_signal_settings(self, input_sig_pars):
        """Upload on the lock-in all the settings for the input signal acquisition.

        Args:
            input_sig_pars (dict): a dictionary containing the input signal parameters,
                including input_channel, range, ac, impedance, and diff.
        """
        in_channel = input_sig_pars["input_channel"]
        for feature, value in input_sig_pars.items(): 
            if feature != "input_channel":
                print("Setting ", feature, "to ", value)
                self.daq.set("/%s/sigins/%d/%s"% (self.device_id,in_channel,feature), value)
        
    def demod_signal_settings(self, demod_pars):
        """Upload on the lock-in all the settings for the demodulators.

        Args:
            demod_pars (dict): a dictionary containing the demodulator parameters,
                including frequency, order, time_constant, and trigger_demod_index.
        """
        for feature, value in demod_pars.items():
            if feature not in ['bandwidth','trigger_demod_index'] :
                print("Setting ", feature, "to ", value)
                self.daq.set("/%s/demods/%d/%s" % (self.device_id, demod_pars["trigger_demod_index"], feature), value)

    def timeconstant_setting(self, demod_pars):
        """Upload on the lock-in the setting for the time constant.

        Args:
            demod_pars (dict): a dictionary containing the demodulator parameters,
                including bandwidth, order, and trigger_demod_index.
        """
        timeconstant = zhinst.utils.bw2tc(demod_pars["bandwidth"], demod_pars["order"])
        print("Setting timeconstant to ", timeconstant)
        self.daq.setDouble("/%s/demods/%d/%s" % (self.device_id,demod_pars["trigger_demod_index"],"timeconstant"), timeconstant)
        # Wait for the demodulator filter to settle.
        timeconstant_settler = self.daq.getDouble(
            "/%s/demods/%d/timeconstant" % (self.device, demod_pars["trigger_demod_index"])
                                            )
        time.sleep(10 * timeconstant_settler)
        # Perform a global synchronization between the device and the data server.
        self.daq.sync()
    
    def oscillator_settings(self, osc_pars):
        """Upload on the lock-in the setting for the oscillator channel.

        Args:
            osc_pars (dict): a dictionary containing the oscillator parameters,
                including osc_index and osc_freq.
        """
        print("Setting frequency to ", osc_pars["osc_freq"])
        self.daq.set("/%s/oscs/%d/freq" % (self.device_id, osc_pars["osc_index"]), osc_pars["osc_freq"])
    
    def evaluate_nrows(self,scan_pars):
        """ evaluate the number of rows of the scan depending on the scan type
        Args:
            scan_pars (dict): a dictionary containing the scan parameters,
                including type and dimension."""
        
        if scan_pars["dim"] == 1: 
            if scan_pars["type"] == "continous":
                return 3
            elif scan_pars["type"] == "discrete":
                return int(np.floor((scan_pars["scan_edges"][1]-scan_pars["scan_edges"][0])/scan_pars["stepsize"])) + 3  # (1 + 2 = 3, 2 for calibration)
            else: 
                raise Exception("Type of scan in input is not valid! Type either continous or discrete.") 
            
        elif scan_pars["dim"] == 2: 
            if scan_pars["type"] == "continous":
                return int(np.floor((scan_pars["servo_scan_edges"][1]-scan_pars["servo_scan_edges"][0])/scan_pars["servo_stepsize"] + 3))   # servo is responsible for discrete motion along lines
            elif scan_pars["type"] == "discrete":
                pixel_per_line = int(np.floor((scan_pars["scan_edges"][1]-scan_pars["scan_edges"][0])/scan_pars["stepsize"])) + 1 
                number_of_line = int(np.floor((scan_pars["servo_scan_edges"][1]-scan_pars["servo_scan_edges"][0])/scan_pars["servo_servo_stepsize"])) + 1
                nrows = pixel_per_line*number_of_line + 2 # + 2 for calibration
                return nrows
            else: 
                raise Exception("Type of scan in input is not valid! Type either continous or discrete.") 
        else:
            raise Exception("Scan dimension parameter (dim) in input is not valid! Type either continous or discrete.") 
        
    def evaluate_burst_duration(self,scan_pars):
        """Evaluate the duration of the scan depending on whether the scan type is continous or discrete"""
        if scan_pars["type"] == "continous": 
            return (scan_pars["scan_edges"][1]-scan_pars["scan_edges"][0])/scan_pars["velocity"]

        else:
            return 0.05 # 50 ms
        
    def evaluate_trigger_edge(self,scan_pars):
        if scan_pars["type"] == "continous":
            return 1 # trig on the positive edge
        else:
            return 2 # trig on the negative edge
            
    def join_data_acquisition_pars(self,data_acquisition_pars,demod_pars,scan_pars):
        """Evaluate some parameters for the data acquisition from demod_pars and scan_pars
        
        Args:
            data_acquisition_pars (dict): a dictionary containing part of the parameters
                    for the data acquisition
            demod_pars (dict): a dictionary containing the parameters for the demudolator
            scan_pars (dict): a dictionary containing the scan parameters.    
        """ 
        num_rows = self.evaluate_nrows(scan_pars)
        burst_duration = self.evaluate_burst_duration(scan_pars)
        trig_edge = self.evaluate_trigger_edge(scan_pars)
        
        self.num_cols = int(np.ceil(demod_pars["rate"]*burst_duration))  
        triggernode = "/%s/demods/%d/sample.TrigIn1" % (self.device_id,demod_pars["trigger_demod_index"])
        dir_to_save = os.getcwd()+"\\"+"Results"

        further_data_acquisition_pars = {
			                    "duration" : burst_duration,
			                    "holdoff/time" : burst_duration,
			                    "triggernode" : triggernode,
			                    "grid/cols" : self.num_cols,
			                    "grid/rows" : num_rows,
			                    "save/directory": dir_to_save,
                                "edge" : trig_edge
                                }
        return {**data_acquisition_pars, **further_data_acquisition_pars}

    def data_acquisition_settings(self,data_acquisition_pars):
        """upload on the lock-in all the settings for data acquisition
        
        Args:
            data_acquisition_pars (dict): a dictionary containing part of the parameters
                    for the data acquisition
        """
        self.daq_module = self.daq.dataAcquisitionModule()
        for feature,value in data_acquisition_pars.items():
            print("Setting ", feature, "to ",value)
            self.daq_module.set(feature,value)
    
    def subscribe_to_signals(self,signal_paths):
        """Subscribes to signal paths of the signal of interest
        
        Args:
            signal_paths (list): a list containing the signal of interests
        """
        self.data = {}
        for signal_path in signal_paths:
            print("Subscribing to ",signal_path)
            self.daq_module.subscribe(signal_path)
            self.data[signal_path] = []
    