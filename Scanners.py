from PI_commands import Stepper
import numpy as np

class Scan1D:
    """Scan designed to perform 1D scan"""
    def __init__(self,InPars):    
        self.PI = InPars["pi"]        
        self.scan_pars = InPars["scan_pars"]
        self.scan_edges = self.scan_pars["scan_edges"]
        self.stepsize = self.scan_pars["stepsize"]
        # evaluate target positions for the 1D scan
        self.targets = self.evaluate_target_positions()
        self.master = Stepper(self.PI["ID"],self.PI["stage_ID"]) 

    def evaluate_target_positions(self):
        """ Evaluate the partition of the target points for a 1D scan   
        """ 
        # calculate targets points
        Npoints = int(abs(self.scan_edges[1]-self.scan_edges[0])/self.stepsize) + 1
        return np.linspace(self.scan_edges[0],self.scan_edges[1],Npoints,endpoint=  True)

    def connect_master(self):
        """ perform all the procedures for setting up properly the PI device""" 
        self.master.connect_pidevice()
    
    def setup_master(self):
        """Set the parameters of interest in the ROM of the device"""
        self.master.set_velocity(self.scan_pars["velocity"])
        self.master.set_acceleration(self.scan_pars["acceleration"])

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
        cur_pos = []
        for target in self.targets:
            self.master.move_stage_to_target(target)        
            print("Position: ", target)
            cur_pos.append(self.master.get_curr_pos())
        return cur_pos

    
    def execute_continuous_1D_scan(self):
        """ Execute the 1D scan by: (1) moving the axis on all the targets positions, 
            (2) measuring the raw_data from the Zurich lock-in (3) moving continously
        """
        self.master.move_stage_to_target(self.targets[-1])        
        