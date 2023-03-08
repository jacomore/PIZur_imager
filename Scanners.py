from PI_commands import Stepper, StepperChain
import numpy as np
import Input_validator as inval

class Scan1D:
    """Scan designed to perform 1D scan"""
    def __init__(self,InPars):    
        self.PI = InPars["pi"]        
        self.scan_pars = InPars["scan_pars"]

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
        self.master = Stepper(self.PI["ID"],self.PI["stage_ID"]) 
        self.master.connect_pidevice()
    
    def setup_1D_PI(self):
        """Set the parameters of interest in the ROM of the device"""
        self.master.set_velocity(self.scan_pars["velocity"])
        # set acceleration ... and many others

    def evaluate_target_positions(self):
        """ Evaluate the partition of the target points for a 1D scan   
        """ 
        # calculate targets points
        Npoints = int((self.scan_edges[1]-self.scan_edges[0])/self.stepsize) + 1
        self.targets =  np.linspace(self.scan_edges[0],self.scan_edges[1],Npoints,endpoint=  True)

    def execute_calibration_step(self):
        """evaluate the calibration step to perform with the master controller"""
        cal_target = abs(self.targets[0] - self.stepsize)
        self.master.move_stage_to_target(cal_target) 

    def init_1D_scan(self):
        """ Setup the 1D scan by: (1) moving the axis on all the targets positions, 
            (2) measuring the raw_data from the Zurich lock-in (3) saving the data on read
        """
        self.master.move_stage_to_ref(self.PI["refmode"])
        self.master.move_stage_to_target(self.targets[0])
        self.master.configure_out_trigger(trigger_type=6)

    def execute_discrete_1D_scan(self):
        """ Execute the 1D scan by: (1) moving the axis on all the targets positions, 
            (2) measuring the raw_data from the Zurich lock-in (3) saving the data on read
        """
        self.init_1D_scan()
        self.execute_calibration_step()
        for target in self.targets:
            self.master.move_stage_to_target(target)        
            print("Position: ", target)
    
    def execute_continous_1D_scan(self):
        """ Execute the 1D scan by: (1) moving the axis on all the targets positions, 
            (2) measuring the raw_data from the Zurich lock-in (3) moving continously
        """
        self.init_1D_scan()
        self.master.move_stage_to_target(self.targets[-1])        
        
class Scan2D:
    """
    Scan2D is designed to control two PI controller and the Zurich lock-in
        with the aim of perfoming a two dimensional scan along the desired axis (x or y). 
    """
    def __init__(self):
         # input parameters as dictionary from json file
        openPars = open('input_dicts.json')
        InPars = json.load(openPars)
        self.PI = InPars["pi"]        
        self.scan_pars = InPars["scan_pars"]

        # connect PI controller
        self.connect_2D_PI()
        # setup PI controller
        self.setup_2D_PI()

        self.axis_edges = self.chain.master.evaluate_axis_edges()
        self.scan_edges = inval.target_within_axis_edges(self.scan_pars["scan_edges"],self.axis_edges)
        self.stepsize = self.scan_pars["stepsize"]
        self.targets = self.evaluate_target_positions(self.scan_edges,self.stepsize)

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
        self.chain.servo.set_velocity(self.scan_pars["velocity_servo"]) # 10 mm/s is the standard velocity of the controller
     
       
    def evaluate_target_positions(self,scanedges,stepsize):
        """ Evaluate the partition of the target points for a 1D scan   
        """ 
        # calculate targets points
        Npoints = int((scanedges[1]-scanedges[0])/stepsize) + 1
        return np.linspace(scanedges[0],scanedges[1],Npoints,endpoint=  True)
                
    def execute_calibration_step(self):
        """evaluate the calibration step to perform with the either the servo or the master controller"""
        if self.scan_pars["main_axis"] == "master":
            cal_target = abs(self.srv_targets[0] - self.srv_stepsize)
            self.chain.servo.move_stage_to_target(cal_target) 
        elif self.scan_pars["main_axis"] == "servo":
            cal_target = abs(self.targets[0] - self.stepsize)
            self.chain.master.move_stage_to_target(cal_target) 
    
    def set_out_trigger(self):
        """Depending on type f scan and the main axis, set the trigger output for the controllers."""
        if self.scan_pars["type"] == "continous":
            if self.scan_pars["main_axis"] == "master":
                self.chain.master.configure_out_trigger(trigger_types=6)
            elif self.scan_pars["main_axis"] == "servo":
                self.chain.servo.configure_out_trigger(trigger_types=6)
        elif self.scan_pars["type"] == "discrete":
            self.chain.configure_both_trig(trigger_types=[6,6])

    def init_2D_scan(self):
        """ Setup the 2D scan
        """
        # move to first target position
        self.chain.master.move_stage_to_ref(self.PI["refmode"])
        self.chain.servo.move_stage_to_ref(self.PI["refmode_servo"])
        self.chain.master.move_stage_to_target(self.targets[0])
        self.chain.servo.move_stage_to_target(self.srv_targets[0])
        # activate trigger signals
        self.set_out_trigger()
    
    def execute_discrete_2D_scan(self):
        """execute the two 2D discrete scan"""
        self.init_2D_scan()
        self.execute_calibration_step()

        if self.scan_pars["main_axis"] == "master":
            for idx_row,row in enumerate(self.srv_targets):
                self.chain.servo.move_stage_to_target(row)
                if (idx_row%2 == 0):
                    for col in self.targets:
                        self.chain.master.move_stage_to_target(col)
                else:
                    for col in self.targets[::-1]:
                        self.chain.master.move_stage_to_target(col)                        

        elif self.scan_pars["main_axis"] == "servo":
            for idx_col,col in enumerate(self.targets):
                self.chain.master.move_stage_to_target(col) 
                if (idx_col%2 == 0):
                    for row in self.srv_targets:
                        self.chain.servo.move_stage_to_target(row)    
                else:
                    for row in self.srv_targets[::-1]:
                        self.chain.servo.move_stage_to_target(row)                 
                
        
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

