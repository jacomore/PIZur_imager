from PI_commands import Stepper
import numpy as np

class Scan1D:
    """A class to perform 1D continuous or discrete scans without the need to understand the 
    lower level class Stepper 
    """
    def __init__(self,InPars):
        """
        Initialize Scan1D object with input parameters.

        Args:
            InPars (dict): Dictionary of input parameters containing the following keys:
                - pi (dict): Dictionary of PI device information.
                - scan_pars (dict): Dictionary of scan parameters containing the following keys:
                    - scan_edges (tuple): Tuple of start and end positions of the scan.
                    - stepsize (float): Step size of the scan.
                    - velocity (float): Velocity of the scan.
                    - acceleration (float): Acceleration of the scan.
        """
        self.PI = InPars["pi"]        
        self.scan_pars = InPars["scan_pars"]
        self.scan_edges = self.scan_pars["scan_edges"]
        self.stepsize = self.scan_pars["stepsize"]
        self.targets = self.evaluate_target_positions()
        self.stepper = Stepper(self.PI["ID"],self.PI["stage_ID"]) 

    def evaluate_target_positions(self):
        """
        Evaluate the partition of the target points for a 1D scan.

        Returns:
            numpy.ndarray: Array of target positions.
        """
        Npoints = int(abs(self.scan_edges[1]-self.scan_edges[0])/self.stepsize) + 1
        return np.linspace(self.scan_edges[0],self.scan_edges[1],Npoints,endpoint=  True)

    def connect_stepper(self):
        """
        Connect to the the PI device through a user-interface I/O.
        """
        self.stepper.connect_pidevice()
    
    def setup_motion_stepper(self):
        """
        Store input velocity and acceleration in the ROM of the device
        """
        self.stepper.set_velocity(self.scan_pars["velocity"])
        self.stepper.set_acceleration(self.scan_pars["acceleration"])

    def init_stepper_scan(self):
        """ 
        Setup the 1D scan in four steps:
                        - acceleration and velocity are set to default values for quick refering and motion 
                        - stage is moved to reference, either positive or negative depending on the input refmode
                        - stage is moved to the first target point
                        - output trigger is selected and activated
        """
        # high default values to obtain a quick referencing 
        self.stepper.set_velocity(10)
        self.stepper.set_acceleration(20)
    
        self.stepper.move_stage_to_ref(self.PI["refmode"])
        self.stepper.move_stage_to_target(self.targets[0])
        trigtype = self.PI["trig_type"]
        self.stepper.configure_out_trigger(trigger_type=trigtype)

    def execute_discrete_scan(self):
        """
        Execute the 1D discrete scan by moving the axis on all the target positions.

        Returns:
            list: List of current positions.
        """
        cur_pos = []
        for target in self.targets:
            self.stepper.move_stage_to_target(target)        
            print("Position: ", target)
            cur_pos.append(self.stepper.get_curr_pos())
        return cur_pos

    
    def execute_continuous_scan(self):
        """
        Execute the continuous scan by moving the axis to the last position.
        """
        self.stepper.move_stage_to_target(self.targets[-1])        
        