import json
from PI_commands import Stepper, StepperChain
from Zhinst_commands import zhinst_lockin
from pipython import pitools
import numpy as np
from Setup_commands import SetupScan
from math import isclose
from time import sleep
import csv

class Scan1D:
    """Scan designed to perform 1D scan"""
    def __init__(self):
        # common features between Scanners
        self.setscan = SetupScan("input_dicts.json") 
        
        self.scan_pars = self.setscan.InPars["scan_pars"]
        self.PI = self.setscan.InPars["pi"]
         
        # setup PI controller
        self.setup_1D_PI()   

        # check input scan edges validity
        self.axis_edges = self.master.evaluate_axis_edges()
        self.scan_edges = self.setscan.target_within_axis_edges(self.scan_pars["scan_edges"],self.axis_edges)
        self.stepsize = self.scan_pars["stepsize"]
        self.targets = self.setscan.evaluate_target_positions(self.scan_edges,self.stepsize)


        # setup zhinst_lockin     
       # self.setscan.setup_lockin()
        
        # setup data_acquisition
       # self.setscan.setup_data_acquisition()
        
        # signal subscrition
       # self.setscan.subscribe_paths()
        
    def setup_1D_PI(self):
        """ perform all the procedures for setting up properly the PI device""" 
        self.master = Stepper(self.PI["ID"],self.PI["stage_ID"]) # correct here and place only self.PI as below, more compact
        self.master.connect_pidevice()
        self.master.set_velocity(self.PI["velocity"])
        #self.master.move_stage_to_ref(self.PI["refmode"])       
        
    def evaluate_calibration_steps(self):
        """evaluate the calibration step to perform with the master controller"""
      #  assert isclose(self.master.get_curr_pos(),self.targets[0],abs_tol=1e-3)
        if self.scan_pars["type"] == "discrete":
            return [abs(self.targets[0] - 2*self.stepsize),abs(self.targets[0] - self.stepsize)]
        else: 
            return [self.targets[-1],self.targets[0]]

    def execute_calibration_steps(self):
        """execute the two intermediate step before the start of the real scan procedure for loading 
           all the parameter into the ROM of the zurich 
        """
        calibration_steps = self.evaluate_calibration_steps()
        print(calibration_steps)
        for target in calibration_steps:
            self.daqmod.read(True)
            self.master.move_stage_to_target(target)
            print(self.setscan.lockin.daq_module.finished())
            print(self.setscan.lockin.daq_module.progress())
            sleep(0.1)


    def setup_1D_scan(self):
        """ Setup the 1D scan by: (1) moving the axis on all the targets positions, 
            (2) measuring the raw_data from the Zurich lock-in (3) saving the data on read
        """
                # rename data_acquisition for readability
        self.daqmod = self.setscan.lockin.daq_module
        self.master.move_stage_to_target(self.targets[0])
        self.master.configure_out_trigger(trigger_type=6)
        self.daqmod.execute()
        self.execute_calibration_steps()
        
    def execute_discrete_1D_scan(self):
        """ Execute the 1D scan by: (1) moving the axis on all the targets positions, 
            (2) measuring the raw_data from the Zurich lock-in (3) saving the data on read
        """
        xdata, ydata = [], []
        print(self.targets)
        self.setup_1D_scan()
        for idx,target in enumerate(self.targets):
            if not  self.daqmod.finished():
                raw_data = self.daqmod.read(True)
                self.master.move_stage_to_target(target)        
                print("Progress:",np.floor(self.daqmod.progress())*100,"%")
                yval = self.process_raw_data(raw_data,idx)
                sleep(0.1)
                
                if yval != []:
                    xdata.append(target)
                    ydata.append(np.mean(yval))
                    print("Position:",target,"Value: ",np.mean(yval))
                    yield ydata,xdata
                print("----------------")
            else:   
                print("Scan is finished")
    
    def execute_continous_1D_scan(self):
        """ Execute the 1D scan by: (1) moving the axis on all the targets positions, 
            (2) measuring the raw_data from the Zurich lock-in (3) moving continously
        """
        xdata = np.linspace(self.targets[0],self.targets[-1],self.setscan.lockin.num_cols)
        self.setup_1D_scan()
        print(self.setscan.lockin.daq_module.finished())
        print(self.setscan.lockin.daq_module.progress())

        raw_data = self.daqmod.read(True)
        self.master.move_stage_to_target(self.targets[-1])
        sleep(0.1)
        ydata = self.process_raw_data(raw_data,0)
        print(ydata,xdata)
        yield ydata,xdata
        
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
        for signal_path in self.setscan.signal_paths:
            for signal_burst in raw_data.get(signal_path.lower(),[]):
                demod_values.append(signal_burst["value"][index,:])

        return demod_values
        
        
class Scan_2D:
    """
    Scan2D is designed to control two PI controller and the Zurich lock-in
        with the aim of perfoming a two dimensional scan along the desired axis (x or y). 
    """
    def __init__(self):
        # common features between Scanners
        self.setscan = SetupScan("input_dicts.json") 
        
        self.scan_pars = self.setscan.InPars["scan_pars"]
        self.PI = self.setscan.InPars["pi"]
  
        
        # setup PI controller
        self.setup_2D_PI()   

        # check input scan edges validity
        self.axis_edges = self.chain.master.evaluate_axis_edges()
        self.scan_edges = self.setscan.target_within_axis_edges(self.scan_pars["scan_edges"],self.axis_edges)
        self.stepsize = self.scan_pars["stepsize"]
        self.targets = self.setscan.evaluate_target_positions(self.scan_edges,self.stepsize)
        
        # same for servo --> explicitely write that is for servo
        self.srv_axis_edges = self.chain.servo.evaluate_axis_edges()
        self.srv_scan_edges = self.setscan.target_within_axis_edges(self.scan_pars["scan_edges_servo"],self.srv_axis_edges)
        self.srv_stepsize = self.scan_pars["stepsize_servo"]
        self.srv_targets = self.setscan.evaluate_target_positions(self.srv_scan_edges,self.srv_stepsize)
        print(self.srv_targets)
        # setup zhinst_lockin     
#        self.setscan.setup_lockin()
        
        # setup data_acquisition
#        self.setscan.setup_data_acquisition()
        
        # signal subscrition
#       self.setscan.subscribe_paths()

    def setup_2D_PI(self):
        """ perform all the procedures for setting up properly the PI device""" 
        self.chain = StepperChain(self.PI["ID"],self.PI["stage_ID"]) # correct here and place only self.PI as below, more compact
        self.chain.connect_daisy([1,2])
        self.chain.master.set_velocity(self.PI["velocity"])
        self.chain.reference_both_stages(ref_modes=["FNL","FNL"])
    
    def evaluate_calibration_steps(self):
        """evaluate the calibration step to perform with the servo controller"""
#        assert isclose(self.chain.servo.get_curr_pos(),self.srv_targets[0],abs_tol=1e-3)
        if self.scan_pars["type"] == "discrete":
            return [abs(self.srv_targets[0] - 2*self.srv_stepsize),abs(self.srv_targets[0] - self.srv_stepsize)]
        else: 
            return [self.targets[-1],self.targets[0]]
        
    def execute_calibration_steps(self):
        """execute the two intermediate step before the start of the real scan procedure for loading 
           all the parameter into the ROM of the zurich 
        """
        calibration_steps = self.evaluate_calibration_steps()
              # rename data_acquisition for readability
        for target in calibration_steps:
            raw_data = self.daqmod.read(True)
            self.chain.master.move_stage_to_target(target)   # execute the calibration step with the servo controller

    def setup_2D_scan(self):
        """ Setup the 2D scan by: (1) moving the axis on all the first targets positions, 
            (2) measuring the raw_data from the Zurich lock-in (3) saving the data on read
        """
        # move to first target position
        self.daqmod = self.setscan.lockin.daq_module
        self.chain.master.move_stage_to_target(self.targets[0])
        self.chain.servo.move_stage_to_target(self.srv_targets[0])
        # activate trigger signals
        self.chain.configure_both_trig(trigger_types=[6,6])
        self.daqmod.execute()
        self.execute_calibration_steps()
        
    def new_row_pixel(self,idx,row):
        """move to a new position with the servo axis. Here, it calculates the value of the intensity and process it (average)"""
        raw_data = self.daqmod.read(True)
        self.chain.servo.move_stage_to_target(row)
        val = self.process_raw_data(raw_data,idx)
        return np.mean(val)
    
    def new_col_pixel(self,idx,col):
        """move to a new position with the master axis. Here, it calculates the value of the intensity and process it (average)"""
      #  raw_data = self.daqmod.read(True)
        self.chain.master.move_stage_to_target(col)
      #  return self.process_raw_data(raw_data,idx)
        
    def execute_discrete_2D_scan(self):
        """execute the two 2D discrete scan"""
        zvalues = []    # matrix that'll be filled with acquired data
        col_idx, col = 0, self.scan_edges[0] # column index is initially zero

        self.setup_2D_scan()
    
        for row_idx,row in self.srv_targets:
            if not self.daqmod.finished():
                idx = (row_idx + 1)*(col_idx + 1)
                val = self.new_row_pixel(idx,row)
                while val != []:
                    sleep(0.01)
                zvalues.append(val)
                yield zvalues
                
                for col_idx,col in self.targets:
                    if not self.daqmod.finished():
                        idx = (row_idx + 1)*(col_idx + 1)   
                        val = self.new_col_pixel(idx,col)
                        
                        if val != []:
                            zvalues.append(val)
                        yield zvalues
                    else: 
                        print("Loop exit on column!")
            else:
                print("loop exit on row!")

    def execute_continous_2D_scan(self):
       # self.setup_2D_scan()
        # with open("test1.txt",mode = 'w',newline = '') as file:
         #   writer  = csv.writer(file)
        self.chain.master.move_stage_to_target(self.targets[0])
        self.chain.servo.move_stage_to_target(self.srv_targets[0])
        # activate trigger signals
        self.chain.configure_both_trig(trigger_types=[6,6])
        for row_idx,row in enumerate(self.srv_targets):
            print(row_idx)
           # if not self.daqmod.finished():
            self.chain.servo.move_stage_to_target(row)               
            if row_idx%2 == 0:
                self.new_col_pixel(row_idx+1,self.targets[-1])
            else:
                self.new_col_pixel(row_idx+1,self.targets[0])
               # sleep(0.1)
               # str_val = [str(element) for element in val]
        #           writer.writerow(str_val)
                #yield (val, row_idx)

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
        for signal_path in self.setscan.signal_paths:
            for signal_burst in raw_data.get(signal_path.lower(),[]):
                demod_values.append(signal_burst["value"][index,:])

        return demod_values