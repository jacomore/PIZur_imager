import zhinst.utils
import time

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
        
    def input_signal_settings(self,in_channel,input_sig_pars):
        """upload on the lock-in all the settings for the input signal acquisition"""
        for feature,value in input_sig_pars.items(): 
            self.daq.set("/%s/sigins/%d/%s"% (self.device_id,in_channel,feature),value)
        
    def demod_signal_settings(self,trigger_demod_index,demod_pars):
        """upload on the lock-in all the settings for the demodulators"""
        for feature,value in demod_pars.items():
            if feature != 'bandwidth':
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
    
    def oscillator_setting(self,osc_index,osc_freq):
        """ upload on the lock-in the setting for the oscillator channel"""
        self.daq.set("/%s/oscs/%d/freq" % (self.device_id, osc_index), osc_freq)

            
    def data_acquisition_setting(self,data_acquisition_pars):
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
    