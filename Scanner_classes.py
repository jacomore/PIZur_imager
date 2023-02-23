import json
from PI_commands import Stepper, StepperChain
from Zhinst_commands import zhinst_lockin
from multiprocessing import Pipe
from pipython import pitools
import numpy as np
from math import isclose
from time import sleep,time
class Scan_1D: 
    """ Scan1D is designed to control a single PI controller and the Zurich lock-in
        with the aim of perfoming one dimensional scan along the desired axis (x or y). 
    """

    def __init__(self,filename):
        """Unpack all the necessary parameters necessary for performing the 1D scan
           and the analysis. Parameters are then instantiated in the instruments by using
           the respective classes. Eventually, 1D scan is performed.

           Arguments
           -------
           filename (str) : name of the file (+ extension) containing all the input data
           dim (int) : integer number that defines the dimensions of the scan. It can be either 1 (one dimensional)
                       or 2 (two dimensional)
        """
        openPars = open(filename)
        self.InPars = json.load(openPars)
        self.PI , self.zurich = self.InPars["pi"], self.InPars["zurich"]
        self.setup_1D_PI()
        # connect and instantiate lock-in: input signals, demodulator, oscillator
        self.setup_lockin()
        # connect and instantiate the data acquisition of the zhinst
        self.setup_data_acquisition()
        # subscribes to signals of interest
        self.subscribe_paths()

    def setup_1D_PI(self):
        """ perform all the procedures for setting up properly the PI device""" 
        self.master = Stepper(self.PI["ID"],self.PI["stage_ID"]) # correct here and place only self.PI as below, more compact
        self.master.connect_pidevice()
        self.master.move_stage_to_ref(self.PI["refmode"])
        self.master.configure_out_trig(type = self.PI["trig_type"])
        self.master.axis_edges = self.master.find_axis_edges()
        self.master.scan_edges = self.target_within_axis_edges(self.PI["master_scan_edges"])
        self.master.stepsize = self.PI["master_stepsize"]

    def input_new_scan_edges(self,scanedges):
        """Asks for and returns new edges for the 1D scan
        """ 
        print(f"Invalid input: desired scan range [{scanedges[0]},{scanedges[1]}] is not within axis range: [{self.master.axis_edges[0]},{self.master.axis_edges[1]}]")
        while True: 
            try:
                neg = float(input("Please, type a new value for the negative edge: "))
                pos = float(input("Please, type a new value for the positive edge: "))
                break
            except ValueError:
                print("That was no valid number!")
        return [neg,pos]

    def target_within_axis_edges(self,scanedges):
        """
        Sorts values of scanedges and, is they are not comprised in axis_edges,
        invokes input_new_edges to get new edges

        Arguments:
        --------
        device (str) : "master" or "servo", to identify the scan edges to which controller is referred
        """ 
        scanedges.sort()
        if (scanedges[0] < self.master.axis_edges[0] or scanedges[1] > self.master.axis_edges[1]):
            scanedges = self.input_new_scan_edges(scanedges) 
            scanedges = self.target_within_axis_edges(scanedges)
        return scanedges

    def evaluate_target_positions(self):
        """ Evaluate the partition of the target points for a 1D scan   
        """ 
        # calculate targets points
        Npoints = int((self.master.scan_edges[1]-self.master.scan_edges[0])/self.master.stepsize) + 1
        if self.PI["motion_direction"] == "FRWD":
            targets =  np.linspace(self.master.scan_edges[0],self.master.scan_edges[1],Npoints,endpoint=  True)
        else:
            targets = np.linspace(self.master.scan_edges[1],self.master.scan_edges[0],Npoints,endpoint=  True)
        return targets
        
    def evaluate_calibration_steps(self):
        """evaluate the two intermediate steps before the start of the real scan procedure for loading 
           all the parameter into the ROM of the zurich 
        """
        first_target = self.evaluate_target_positions()[0]
        curr_pos =  self.master.pidevice.qPOS(self.master.pidevice.axes)['1']
        delta_x = first_target - curr_pos
        if isclose(delta_x,0.,abs_tol=1e-4):   # reference point is the same as the starting point of the scan
            return [abs(curr_pos - 2*self.master.stepsize),abs(curr_pos - self.master.stepsize)]
        elif delta_x > 0:                      # negative reference, point is in a forward position
            return [delta_x/3.0 , 2.*delta_x/3.]
        elif delta_x < 0: 
            return [curr_pos + delta_x/3. , curr_pos + 2*delta_x/3.]

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
                                                                        self.PI
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

    def execute_calibration_steps(self):
        """execute the two intermediate step before the start of the real scan procedure for loading 
           all the parameter into the ROM of the zurich 
        """
        calibration_steps = self.evaluate_calibration_steps()
        for target in calibration_steps:
            self.lockin.daq_module.read(True)
            self.master.pidevice.MOV(self.master.pidevice.axes,target)
            pitools.waitontarget(self.master.pidevice)

    def execute_1D_scan(self):
        """ Execute the 1D scan by: (1) moving the axis on all the targets positions, 
            (2) measuring the raw_data from the Zurich lock-in (3) saving the data on read
        """
        xdata,ydata = [],[]
        targets = self.evaluate_target_positions()
        self.lockin.daq_module.execute()
        self.execute_calibration_steps()
        for index,target in enumerate(targets): 
            if not self.lockin.daq_module.finished():
                raw_data = self.lockin.daq_module.read(True)
                self.master.pidevice.MOV(self.master.pidevice.axes,target)
                pitools.waitontarget(self.master.pidevice)
                print("Position:",target,"Progress:",np.floor(self.lockin.daq_module.progress()[0])*100,"%")
                yval = self.process_raw_data(raw_data,index)
                if yval != []:
                    xdata.append(target)
                    ydata.append(yval)
                    yield ydata,xdata
            else:   
                print("Scan is finished; data are saved in:", self.complete_daq_pars["save/directory"])

    def process_raw_data(self,raw_data,index):
        """Gets and process raw_rata and updates data value

        Parameters
        ----------
        raw_data : dict
            dictionary in which read data are stored
        index : int
            number that contains the number of step of the scan so far

        Returns
        -------
        average value 
        """
        demod_values = []
        for signal_path in self.signal_paths:
            for signal_burst in raw_data.get(signal_path.lower(),[]):
                demod_values.append(np.mean(signal_burst["value"][index,:]))

        return demod_values
        
class Scan_2D:
    """
    Scan2D is designed to control two PI controller and the Zurich lock-in
        with the aim of perfoming a two dimensional scan along the desired axis (x or y). 
    """
    def __init__(self,filename):
        """Unpack all the necessary parameters necessary for performing the 1D scan
           and the analysis. Parameters are then instantiated in the instruments by using
           the respective classes. Eventually, 1D scan is performed.

           Arguments
           -------
           filename (str) : name of the file (+ extension) containing all the input data
        """
        openPars = open(filename)
        self.InPars = json.load(openPars)
        self.PI , self.zurich = self.InPars["pi"], self.InPars["zurich"]
        self.setup_2D_PI()
        # connect and instantiate lock-in: input signals, demodulator, oscillator
        self.setup_lockin()
        # connect and instantiate the data acquisition of the zhinst
        self.setup_data_acquisition()
        # subscribes to signals of interest
        self.subscribe_paths()

    def setup_2D_PI(self):
        """ perform all the procedures for setting up properly the PI device""" 
        self.twodev = StepperChain(self.PI["ID"],self.PI["stage_ID"]) # correct here and place only self.PI as below, more compact
        self.twodev.connect_daisy([1,2])
        self.twodev.reference_both_stages(refmodes=[self.PI["refmode_master"],self.PI["refmode_servo"]])
        self.twodev.master.axis_edges = self.twodev.master.find_axis_edges()
        self.twodev.master.scan_edges = self.target_within_axis_edges(self.PI["master_scan_edges"],self.twodev.master.axis_edges)
        self.twodev.master.stepsize = self.PI["master_stepsize"]
        self.twodev.servo.axis_edges = self.twodev.servo.find_axis_edges()
        self.twodev.servo.scan_edges = self.target_within_axis_edges(self.PI["servo_scan_edges"],self.twodev.servo.axis_edges)
        self.twodev.servo.stepsize = self.PI["servo_stepsize"]

    def input_new_scan_edges(self,scanedges,axisedges):
        """Asks for and returns new edges for the 1D scan
        """ 
        print(f"Invalid input: desired scan range [{scanedges[0]},{scanedges[1]}] is not within axis range: [{axisedges[0]},{axisedges[1]}]")
        while True: 
            try:
                neg = float(input("Please, type a new value for the negative edge: "))
                pos = float(input("Please, type a new value for the positive edge: "))
                break
            except ValueError:
                print("That was no valid number!")
        return [neg,pos]

    def target_within_axis_edges(self,scanedges,axisedges):
        """
        Sorts values of scan_edges and, is they are not comprised in axis_edges,
        invokes input_new_edges to get new edges

        Arguments:
        --------
        device (str) : "master" or "servo", to identify the scan edges to which controller is referred
        """ 
        scanedges.sort()
        if (scanedges[0] < axisedges[0] or scanedges[1] > axisedges[1]):
            scanedges = self.input_new_scan_edges(scanedges,axisedges) 
            scanedges = self.target_within_axis_edges(scanedges,axisedges)
        return scanedges

    def evaluate_target_positions(self,scanedges,stepsize):
        """ Evaluate the partition of the target points for a 1D scan   
        """ 
        # calculate targets points
        Npoints = int((scanedges[1]-scanedges[0])/stepsize) + 1
        if self.PI["motion_direction"] == "FRWD":
            targets =  np.linspace(scanedges[0],scanedges[1],Npoints,endpoint=  True)
        else:
            targets = np.linspace(scanedges[1],scanedges[0],Npoints,endpoint=  True)
        return targets

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
                                                                        self.PI
                                                                        )
        self.lockin.data_acquisition_settings(self.complete_daq_pars)

    def subscribe_paths(self):
        demod_pars = self.InPars["demod_pars"]
        demod_path = f"/{self.zurich['device_id']}/demods/{demod_pars['trigger_demod_index']}/sample"
        self.signal_paths = []
        self.signal_paths.append(demod_path + ".R.avg") # this should be given as input!
        #signal_paths.append(demod_path + ".Theta.avg")  # this should be made an input!
        self.signal_paths.append(self.complete_daq_pars["triggernode"])  
        self.lockin.subscribe_to_signals(self.signal_paths)

    def execute_calibration_steps(self,master_target,master_stepsize,servo_target):
        # move master and servo to initial position
        self.twodev.master.pidevice.MOV(self.twodev.master.pidevice.axes,master_target)
        self.twodev.servo.pidevice.MOV(self.twodev.servo.pidevice.axes,servo_target)
        pitools.waitontarget(self.twodev.master.pidevice)
        pitools.waitontarget(self.twodev.servo.pidevice)
        # configure triggers
        self.twodev.configure_both_trig(types = [self.PI["trig_type_master"],self.PI["trig_type_servo"]])

    def execute_2D_discrete_scan(self):
        servo_pos,master_pos,values = [],[], []

        master_targets = self.evaluate_target_positions(self.twodev.master.scan_edges,self.twodev.master.stepsize)
        servo_targets = self.evaluate_target_positions(self.twodev.master.scan_edges,self.twodev.servo.stepsize)

        self.lockin.daq_module.execute()
        self.execute_calibration_steps(master_targets[0],self.twodev.master.stepsize,servo_targets[0])
        
        row_index = 0
        col_index = 0
        col = 0
        print(master_targets)
        for row in master_targets:
            if not self.lockin.daq_module.finished():
                raw_data = self.lockin.daq_module.read(True)
                self.twodev.master.pidevice.MOV(self.twodev.master.pidevice.axes,row)
                pitools.waitontarget(self.twodev.master.pidevice)
                sleep(0.1)
                z_val = self.process_raw_data(raw_data,(row_index+1)*(col_index+1))
                if z_val != []:
                    print("row:",row,"col:",col,"value:",z_val)
                    master_pos.append(row)
                    values.append(z_val[0])
                    servo_pos.append(col)
                    yield values,master_pos,servo_pos
                row_index = row_index + 1
                for col in servo_targets:
                        if not self.lockin.daq_module.finished():
                            raw_data = self.lockin.daq_module.read(True)
                            self.twodev.servo.pidevice.MOV(self.twodev.servo.pidevice.axes,row)
                            pitools.waitontarget(self.twodev.servo.pidevice)
                            z_val = self.process_raw_data(raw_data,(row_index+1)*(col_index+1))
                            if z_val != []:
                                print("row:",row,"col:",col,"value:",z_val)
                                master_pos.append(row)
                                servo_pos.append(col)
                                values.append(z_val[0])
                                yield values,master_pos,servo_pos
                                print("Progress:",np.floor(self.lockin.daq_module.progress()[0])*100,"%")
                                self.twodev.servo.scan_edges = np.flip(self.twodev.master.scan_edges)
                            else:   
                                print("Scan is finished; data are saved in:", self.complete_daq_pars["save/directory"])
            else:   
                print("Scan is finished; data are saved in:", self.complete_daq_pars["save/directory"])

    def execute_2D_continous_scan(self):
        servo_pos,master_pos, values = [],[],[]

        master_targets = self.evaluate_target_positions(self.twodev.master.scan_edges,self.twodev.master.stepsize)
        servo_targets = self.evaluate_target_positions(self.twodev.master.scan_edges,self.twodev.servo.stepsize)

        self.lockin.daq_module.execute()
        self.execute_calibration_steps(master_targets[0],self.twodev.master.stepsize,servo_targets[0])
        
        self.twodev.master.pidevice.VEL('1',10)

        for row_index,row in enumerate(servo_targets):
            if not self.lockin.daq_module.finished():
                self.twodev.servo.pidevice.MOV(self.twodev.servo.pidevice.axes,row)
                pitools.waitontarget(self.twodev.master.pidevice)
                raw_data = self.lockin.daq_module.read(True)
                self.twodev.master.pidevice.MOV(self.twodev.master.pidevice.axes,self.twodev.master.scan_edges[1])
                pitools.waitontarget(self.twodev.servo.pidevice)
                z_val = self.process_raw_data(raw_data,(row_index))
                if z_val != []:
                    print("row:",row,"value:",z_val[0][:10])
                    print("trig val:",z_val[1])
                    values.append(z_val[0])
                    yield values,row_index
                    print("Progress:",np.floor(self.lockin.daq_module.progress()[0])*100,"%")
                    self.twodev.master.scan_edges = np.flip(self.twodev.master.scan_edges)
            else:   
                    print("Scan is finished; data are saved in:", self.complete_daq_pars["save/directory"])
    

    def process_raw_data(self,raw_data,index):
        """Gets and process raw_rata and updates data value

        Parameters
        ----------
        raw_data : dict
            dictionary in which read data are stored
        index : int
            number that contains the number of step of the scan so far

        Returns
        -------
        average value 
        """
        demod_values = []
        for signal_path in self.signal_paths:
            for signal_burst in raw_data.get(signal_path.lower(),[]):
                demod_values.append(signal_burst["value"][index,:])

        return demod_values