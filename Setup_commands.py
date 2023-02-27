import json
from Zhinst_commands import zhinst_lockin
import numpy as np
from PI_commands import Stepper

class SetupScan: 
    """ SetupPI is designed to setup  the scan parameters of the PI controllers provided by the the "input_dicts.json" file. 
        Hence, additional parameters are calculated on the fly to automatically setup the appropriate environment for the scan procedure.  
    """

    def __init__(self,filename):
        """Unpack all the necessary parameters necessary for setting up the parameters of interest.

           Arguments
           -------
           filename (str) : name of the file (+ extension) containing all the input data
        """
        openPars = open(filename)
        self.InPars = json.load(openPars)
        
        
    def setup_1D_PI(self):
        """ perform all the procedures for setting up properly the PI device""" 
        self.master = Stepper(self.PI["ID"],self.PI["stage_ID"]) # correct here and place only self.PI as below, more compact
        self.master.connect_pidevice()
        self.master.set_velocity(self.PI["velocity"])
        self.master.move_stage_to_ref(self.PI["refmode"])   
        self.master.configure_out_trigger(trigger_type=6)    
        
           
    def input_new_scan_edges(self,scanedges,axisedges):
        """Asks for and returns new edges for the 1D scan
        """ 
        print(f"Invalid input: desired scan range [{scanedges[0]},{scanedges[1]}] is not within axis range: [{axisedges[0]},{axisedges[1]}]")
        while True: 
            try:
                neg = float(input("Please, type a new value for the negative edge: "))
                pos = float(input("Please, type a new value for the positive edge: "))
                new_scanedges = [neg,pos]
                new_scanedges.sort()
                break
            except ValueError:
                print("That was no valid number!")
        return new_scanedges

    def target_within_axis_edges(self,scanedges,axisedges):
        """
        Sorts values of scanedges and, is they are not comprised in axis_edges,
        invokes input_new_edges to get new edges

        Arguments:
        --------
        device (str) : "master" or "servo", to identify the scan edges to which controller is referred
        """ 
        scanedges.sort()
        while (scanedges[0] < axisedges[0] or scanedges[1] > axisedges[1]):
            scanedges = self.input_new_scan_edges(scanedges,axisedges) 
        return scanedges
        
    def evaluate_target_positions(self,scanedges,stepsize,first = False):
        """ Evaluate the partition of the target points for a 1D scan   
        """ 
        # calculate targets points
        Npoints = int((scanedges[1]-scanedges[0])/stepsize) + 1
        if self.PI["motion_direction"] == "FRWD":
            if first:
                return scanedges[0]
            else:
                np.linspace(scanedges[0],scanedges[1],Npoints,endpoint=  True)
        else:
            if first:
                return scanedges[1]
            else:
                return np.linspace(scanedges[1],scanedges[0],Npoints,endpoint=  True)
        
    def setup_lockin(self):
        """ perform all the procedures for setting up properly the lock in: input signals, oscillator, demodulator""" 
        self.lockin = zhinst_lockin(self.zurich) 
        self.lockin.input_signal_settings(self.InPars["input_signal_pars"])
        self.lockin.oscillator_settings(self.InPars["oscillator_pars"])
        self.lockin.demod_signal_settings(self.InPars["demod_pars"])
    
    def setup_data_acquisition(self):
        """ perform all the procedures for setting up properly the data_acquisition tab of the lockin"""
        self.complete_daq_pars = self.lockin.join_data_acquisition_pars(
                                                                        self.InPars["data_acquisition_pars"],
                                                                        self.InPars["demod_pars"],
                                                                        self.InPars["scan_pars"]
                                                                        )
        self.lockin.data_acquisition_settings(self.complete_daq_pars)

    def subscribe_paths(self):
        demod_pars = self.InPars["demod_pars"]
        demod_path = f"/{self.zurich['device_id']}/demods/{demod_pars['trigger_demod_index']}/sample"
        self.signal_paths = []
        self.signal_paths.append(demod_path + ".R.avg") # this should be given as input!
        #signal_paths.append(demod_path + ".Theta.avg")  # this should be made an input!
        #self.signal_paths.append(self.complete_daq_pars["triggernode"])  
        self.lockin.subscribe_to_signals(self.signal_paths)