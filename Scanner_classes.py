import json
from PI_commands import Stepper
from Zhinst_commands import zhinst_lockin

class Scan1D: 
    """ Scan1D is designed to control a single PI controller and the Zurich lock-in
        with the aim of perfoming one dimensional scan along the desired axis (x or y). 
    """

    def __init__(self,filename):
        """Unpack all the necessary parameters necessary for performing the 1D scan
           and the analysis. Parameters are then instantiated in the instruments by using
           the respective classes. Eventually, 1D is performed.

           Arguments
           -------
           filename (str) : name of the file (+ extension) containing all the input data
        """
        openPars = open(filename)
        self.InPars = json.load(openPars)
        self.PI , self.zurich = self.InPars["pi"], self.InPars["zurich"]
        # connect and instantiate the pi device 
        self.setup_PI()
        # connect and instantiate lock-in: input signals, demodulator, oscillator
        self.setup_lockin()
        # connect and instantiate the data acquisition of the zhinst
        self.setup_data_acquisition()

    def setup_PI(self):
        """ perform all the procedures for setting up properly the PI device""" 
        self.master = Stepper(self.PI["ID"],self.PI["stage_ID"]) # correct here and place only self.PI as below, more compact
        self.master.connect_pidevice()
        self.master.move_stage_to_ref(self.PI["refmode"])
        self.master.configure_out_trig(type = self.PI["trigger_type"])

    def setup_lockin(self):
        """ perform all the procedures for setting up properly the lock in: input signals, oscillator, demodulator""" 
        input_sig_pars,  osc_pars = self.InPars["input_signal_pars"] , self.InPars["oscillator_pars"]
        self.demod_pars = self.InPars["demod_pars"]
        self.lockin = zhinst_lockin(self.zurich) 
        self.lockin.input_signal_settings(input_sig_pars)
        self.lockin.oscillator_settings(osc_pars)
        self.lockin.demod_signal_settings(self.demod_pars)
    
    def setup_data_acquisition(self):
        """ perform all the procedures for setting up properly the PI device"""
        data_acquisition_pars = self.InPars["data_acquisition_pars"] 
        self.complete_daq_pars = self.lockin.join_data_acquisition_pars(
                                                                        data_acquisition_pars,
                                                                        self.demod_pars,
                                                                        self.PI
                                                                        )
        self.lockin.data_acquisition_settings(self.complete_daq_pars)
        demod_path = f"/{self.zurich['device_id']}/demods/{self.demod_pars['trigger_demod_index']}/sample"
        signal_paths = []
        signal_paths.append(demod_path + ".R.avg") # this should be made an input!
        signal_paths.append(demod_path + ".Theta.avg")  # this should be made an input!
        signal_paths.append(data_acquisition_pars["triggernode"])  
        self.lockin.subscribe_to_signals(signal_paths)
