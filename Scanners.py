from PI_commands import Stepper, StepperChain
import numpy as np
import Input_validator as inval
import json

class Scanner:
    """Scan designed to perform 1D scan"""
    def __init__(self):    
        # input parameters as dictionary from json file
        openPars = open('input_dicts.json')
        self.InPars = json.load(openPars)
        self.PI = self.InPars["pi"]        
        self.scan_pars = self.InPars["scan_pars"]

        # connect 1D device
        self.connect_1D_PI()   
        # set properties of the motion and of the devices
        self.setup_1D_PI()
        # check input scan edges validity and defines new attributes
        self.axis_edges = self.master.evaluate_axis_edges()
        self.scan_edges = inval.target_within_axis_edges(self.scan_pars["scan_edges"],self.axis_edges)
        self.stepsize = self.scan_pars["stepsize"]
        self.evaluate_target_positions()

    def connect_1D_PI(self):
        """ perform all the procedures for setting up properly the PI device""" 
        self.master = Stepper(self.PI["ID"],self.PI["stage_ID"]) # correct here and place only self.PI as below, more compact
        self.master.connect_pidevice()
    
    def setup_1D_PI(self):
        """Set the parameters of interest in the ROM of the device"""
        self.master.set_velocity(self.PI["velocity"])

    def evaluate_target_positions(self):
        """ Evaluate the partition of the target points for a 1D scan   
        """ 
        # calculate targets points
        Npoints = int((self.scanedges[1]-self.scanedges[0])/self.stepsize) + 1
        if self.PI["motion_direction"] == "FRWD":
            self.targets =  np.linspace(self.scanedges[0],self.scanedges[1],Npoints,endpoint=  True)
        else:
            self.targets = np.linspace(self.scanedges[1],self.scanedges[0],Npoints,endpoint=  True)

    def perform_calibration_step(self):
        """evaluate the calibration step to perform with the master controller"""
        cal_target = abs(self.targets[0] - self.stepsize)
        self.master.move_stage_to_target(cal_target) 

    def init_1D_scan(self):
        """ Setup the 1D scan by: (1) moving the axis on all the targets positions, 
            (2) measuring the raw_data from the Zurich lock-in (3) saving the data on read
        """
        self.master.move_stage_to_target(self.targets[0])
        self.master.configure_out_trigger(trigger_type=6)

    def execute_discrete_1D_scan(self):
        """ Execute the 1D scan by: (1) moving the axis on all the targets positions, 
            (2) measuring the raw_data from the Zurich lock-in (3) saving the data on read
        """
        self.init_1D_scan()
        self.perform_calibration_step()
        for target in self.targets:
            self.master.move_stage_to_target(target)        
            print("Position: ", target)
    
    def execute_continous_1D_scan(self):
        """ Execute the 1D scan by: (1) moving the axis on all the targets positions, 
            (2) measuring the raw_data from the Zurich lock-in (3) moving continously
        """
        self.setup_1D_scan()
        self.master.move_stage_to_target(self.targets[-1])        
        
class Scan_2D:
    """
    Scan2D is designed to control two PI controller and the Zurich lock-in
        with the aim of perfoming a two dimensional scan along the desired axis (x or y). 
    """
    def __init__(self):
         # input parameters as dictionary from json file
        openPars = open('input_dicts.json')
        self.InPars = json.load(openPars)
        self.PI = self.InPars["pi"]        
        self.scan_pars = self.InPars["scan_pars"]

        # connect PI controller
        self.connect_2D_PI()
        # setup PI controller
        self.setup_2D_PI()

        # check input scan edges validity
        self.axis_edges = self.chain.master.evaluate_axis_edges()
        self.scan_edges = inval.target_within_axis_edges(self.scan_pars["scan_edges"],self.axis_edges)
        self.stepsize = self.scan_pars["stepsize"]
        self.targets = self.evaluate_target_positions(self.scan_edges,self.stepsize)

        # same for servo --> explicitely write that is for servo
        self.srv_axis_edges = self.chain.servo.evaluate_axis_edges()
        self.srv_scan_edges = inval.target_within_axis_edges(self.scan_pars["scan_edges_servo"],self.srv_axis_edges)
        self.srv_stepsize = self.scan_pars["stepsize_servo"]
        self.srv_targets = self.evaluate_target_positions(self.srv_scan_edges,self.srv_stepsize)

    def connect_2D_PI(self):
        """ perform all the procedures for setting up properly the PI device""" 
        self.chain = StepperChain(self.PI["ID"],self.PI["stage_ID"]) # correct here and place only self.PI as below, more compact
        self.chain.connect_daisy([1,2])

    def setup_2D_PI(self):  
        self.chain.master.set_velocity(self.PI["velocity"])
    
    def evaluate_target_positions(self,scanedges,stepsize):
        """ Evaluate the partition of the target points for a 1D scan   
        """ 
        # calculate targets points
        Npoints = int((scanedges[1]-scanedges[0])/stepsize) + 1
        if self.PI["motion_direction"] == "FRWD":
            return np.linspace(scanedges[0],scanedges[1],Npoints,endpoint=  True)
        else:
            return np.linspace(scanedges[1],scanedges[0],Npoints,endpoint=  True)
        
    def perform_calibration_step(self):
        """evaluate the calibration step to perform with the servo controller"""
        if self.scan_pars["main_axis"] == "master":
            cal_target = abs(self.srv_targets[0] - self.srv_stepsize)
            self.chain.servo.move_stage_to_target(cal_target) 
        elif self.scan_pars["main_axis"] == "servo":
            cal_target = abs(self.targets[0] - self.stepsize)
            self.chain.master.move_stage_to_target(cal_target) 

    def init_2D_scan(self):
        """ Setup the 2D scan by: (1) moving the axis on all the first targets positions, 
            (2) measuring the raw_data from the Zurich lock-in (3) saving the data on read
        """
        # move to first target position
        self.chain.master.move_stage_to_target(self.targets[0])
        self.chain.servo.move_stage_to_target(self.srv_targets[0])
        # activate trigger signals
        self.chain.configure_both_trig(trigger_types=[6,6])
    

    def execute_discrete_2D_scan(self):
        """execute the two 2D discrete scan"""
        self.init_2D_scan()
        self.perform_calibration_step()

        if self.scan_pars["main_axis"] == "master":
            for row in self.srv_targets:
                self.chain.servo.move_stage_to_target(row)              
                for col in self.targets:
                    self.chain.master.move_stage_to_ref(col)                        

        elif self.scan_pars["main_axis"] == "servo":
            for col in self.targets:
                self.chain.master.move_stage_to_target(col)              
                for row in self.srv_targets:
                    self.chain.servo.move_stage_to_ref(row)    
        
    def execute_continous_2D_scan(self):
        """execute the 2D continous scan"""
        self.init_2D_scan()
        if self.scan_pars["main_axis"] == "master":
            for row_idx,row in enumerate(self.srv_targets):
                self.chain.servo.move_stage_to_target(row)               
            if row_idx%2 == 0:
                self.chain.master.move_stage_to_ref(self.targets[-1])
            else:
                self.chain.master.move_stage_to_ref(self.targets[0])

        elif self.scan_pars["main_axis"] == "servo":
            for col_idx,col in enumerate(self.targets):
                self.chain.master.move_stage_to_target(col)               
                if col_idx%2 == 0:
                        self.chain.servo.move_stage_to_ref(self.srv_targets[-1])
                else:
                        self.chain.servo.move_stage_to_ref(self.srv_targets[0])

