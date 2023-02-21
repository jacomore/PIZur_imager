import json
from PI_commands import Stepper
from Zhinst_commands import zhinst_lockin
from multiprocessing import Pipe
from pipython import pitools
import numpy as np

from math import isclose

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
        # verify correctness of the input parameters
        self.target_within_axis_edges()

    def setup_PI(self):
        """ perform all the procedures for setting up properly the PI device""" 
        self.master = Stepper(self.PI["ID"],self.PI["stage_ID"]) # correct here and place only self.PI as below, more compact
        self.master.connect_pidevice()
        self.master.move_stage_to_ref(self.PI["refmode"])
        self.master.configure_out_trig(type = self.PI["trig_type"])

    def setup_lockin(self):
        """ perform all the procedures for setting up properly the lock in: input signals, oscillator, demodulator""" 
        self.input_sig_pars,  osc_pars = self.InPars["input_signal_pars"] , self.InPars["oscillator_pars"]
        self.demod_pars = self.InPars["demod_pars"]
        self.lockin = zhinst_lockin(self.zurich) 
        self.lockin.input_signal_settings(self.input_sig_pars)
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
        self.signal_paths = []
        self.signal_paths.append(demod_path + ".R.avg") # this should be made an input!
        #signal_paths.append(demod_path + ".Theta.avg")  # this should be made an input!
        self.signal_paths.append(self.complete_daq_pars["triggernode"])  
        self.lockin.subscribe_to_signals(self.signal_paths)

    def input_new_scan_edges(self):
        """Asks for and returns new edges for the 1D scan
        
        Parameters
        ----------
        axis_edges : list
            Two float elements with the physical edges of the axes
        """ 
        print(f"Invalid input: desired scan range [{self.scan_edges[0]},{self.scan_edges[1]}] is not within axis range: [{self.axis_edges[0]},{self.axis_edges[1]}]")
        while True: 
            try:
                neg = float(input("Please, type a new value for the negative edge: "))
                pos = float(input("Please, type a new value for the positive edge: "))
                break
            except ValueError:
                print("That was no valid number!")
        self.scan_edges_edges = [neg,pos]

    def target_within_axis_edges(self):
        """
        Sorts values of scan_edges and, is they are not comprised in axis_edges,
        invokes input_new_edges to get new edges
        """ 
        self.scan_edges = self.PI["scan_edges"]
        print("Input scan edges are: ",self.scan_edges)
        self.axis_edges = self.master.axis_edges()
        self.scan_edges.sort()
        if (self.scan_edges[0] < self.axis_edges[0] or self.scan_edges[1] > self.axis_edges[1]):
            self.input_new_scan_edges(self.scan_edges,self.axis_edges) 
            self.target_within_axis_edges(self.scan_edges,self.axis_edges)

    def evaluate_target_positions(self):
        """ Evaluate the partition of the target points for a 1D scan   
        """ 
        Npoints = int((self.scan_edges[1]-self.scan_edges[0])/self.PI["stepsize"]) + 1
        if self.PI["motion_direction"] == "FRWD":
            self.targets = np.linspace(self.scan_edges[0],self.scan_edges[1],Npoints,endpoint=  True)
        elif self.PI["motion_direction"] == "BCWD":
            self.targets = np.linspace(self.scan_edges[1],self.scan_edges[0],Npoints,endpoint=  True)

    def evaluate_delta_x(self):
        """evaluate the first target of the scan (first_target) and the reference target (ref_target)
        """
        # evaluate first target 
        if self.PI["motion_direction"] == "FRWD":
            first_target = self.scan_edges[0]
        elif self.PI["motion_direction"] == "BCWD":
            first_target = self.scan_edges[1]
        # evaluate current position
        if self.PI["refmode"] == "FNL":
            ref_target = self.axis_edges[0]
        if self.PI["refmode"] == "FPL":
            ref_target = self.axis_edges[1]

        return first_target, ref_target        
        
    def evaluate_calibration_steps(self):
        """evaluate the two intermediate step before the start of the real scan procedure for loading 
           all the parameter into the ROM of the zurich 
        """
        first_target, ref_target = self.evaluate_delta_x()
        delta_x = first_target - ref_target
        stepsize = self.PI["stepsize"]
        if isclose(delta_x,0.,abs_tol=1e-4):   # reference point is the same as the starting point of the scan
            return [abs(ref_target - 2*stepsize),abs(ref_target - stepsize)]
        elif delta_x > 0:                      # negative reference, point is in a forward position
            return [delta_x/3.0 , 2.*delta_x/3.]
        elif delta_x < 0: 
            return [ref_target + delta_x/3. , ref_target + 2*delta_x/3.]

    def execute_calibration_steps(self):
        """execute the two intermediate step before the start of the real scan procedure for loading 
           all the parameter into the ROM of the zurich 
        """
        calibration_steps = self.evaluate_calibration_steps()
        for target in calibration_steps:
            raw_data = self.daq1D.read(True)
            self.dev1D.MOV(self.dev1D.axes,target)
            pitools.waitontarget(self.dev1D)
            print(raw_data)
            print(target)

    def process_raw_data(self,raw_data,index):
        """Gets and process raw_rata and updates data value

        Parameters
        ----------
        raw_data : dict
            dictionary in which read data are stored
        print_cols : index
            index : int
            number that contains the number of step of the scan so far

        Returns
        -------
        average value 
        """
        for signal_path in self.signal_paths:
            for signal_burst in raw_data.get(signal_path.lower(),[]):
                value = signal_burst["value"][index,:]
                return np.mean(value)
