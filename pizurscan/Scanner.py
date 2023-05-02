from PI_commands import Stepper
import numpy as np

class Scanner:
    """
    A class for performing a 1D scan using a PI device.

    Attributes:
        PI (dict): Dictionary of PI device information.
        scan_pars (dict): Dictionary of scan parameters.
        scan_edges (tuple): Tuple of start and end positions of the scan.
        stepsize (float): Step size of the scan.
        targets (numpy.ndarray): Array of target positions for the scan.
        stepper (Stepper): Stepper object for controlling the PI device.

    Methods:
        __init__(self, InPars):
            Initializes Scan1D object with input parameters.
        evaluate_target_positions(self):
            Evaluates the partition of the target points for a 1D scan.
            Returns:
                numpy.ndarray: Array of target positions.
        connect_stepper(self):
            Connects to the PI device through a user-interface I/O.
        setup_motion_stepper(self):
            Stores input velocity and acceleration in the ROM of the device.
        init_stepper_scan(self):
            Sets up the 1D scan in four steps.
        execute_discrete_scan(self):
            Executes the 1D discrete scan by moving the axis on all the target positions.
            Returns:
                list: List of current positions.
        execute_continuous_scan(self):
            Executes the continuous scan by moving the axis to the last position.
    """

    def __init__(self, InPars):
        """ Initializes Scanner object with input parameters.
        
        Parameters:
        ----------
        - InPars : dict
            a dictionary of input parameters regarding the scan features
        
        Attributes:
        ----------
        - PI : dict
            a dictionary containing the PI controller and axis id
        - scan_pars: dict
            a dictionary containing the scan parameters
        - scan_edges : list
            a list containing the two edges of the scan. Axis will move from the leftward to the rightward.
        - stepsize : float
            a float containing the step size of the scan
        - targets : numpy.array
            a numpy.array containing the targets positions of the scan
        - stepper: Stepper
            a stepper object that instantiate Stepper class.
        """
        self.PI = InPars["pi"]
        self.scan_pars = InPars["scan_pars"]
        self.scan_edges = self.scan_pars["scan_edges"]
        self.stepsize = self.scan_pars["stepsize"]
        self.targets = self.evaluate_target_positions()
        self.stepper = Stepper(self.PI["ID"], self.PI["stage_ID"])

    def evaluate_target_positions(self):
        """
        Evaluates the partition of the target points for a 1D scan.

        Returns:
        --------
        numpy.ndarray: Array of target positions.
        """
        Npoints = int(abs(self.scan_edges[1] - self.scan_edges[0]) / self.stepsize) + 1
        return np.linspace(self.scan_edges[0], self.scan_edges[1], Npoints, endpoint=True)

    def connect_stepper(self):
        """
        Connects to the PI device through a user-interface I/O.
        """
        self.stepper.connect_pidevice()

    def setup_motion_stepper(self):
        """
        Stores input velocity and acceleration in the ROM of the device.
        """
        self.stepper.set_velocity(self.scan_pars["velocity"])
        self.stepper.set_acceleration(self.scan_pars["acceleration"])
        
    def init_stepper_scan(self):
        """Setup the 1D scan in four steps: (1) acceleration and velocity are set to
        default values for quick refering and motion. (2) Stage is moved to reference,
        either positive or negative depending on the input refmode. (3) stage is moved 
        to the first target point output trigger is selected and activated
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
        --------
        list : List of current positions.
        """
        cur_pos = []
        for target in self.targets:
            self.stepper.move_stage_to_target(target)        
            print("Position: ", target)
            cur_pos.append(self.stepper.get_curr_pos())
        self.stepper.close_connection()
        return cur_pos

    
    def execute_continuous_scan(self):
        """
        Execute the continuous scan by moving the axis to the last position.
        """
        self.stepper.move_stage_to_target(self.targets[-1])    
        self.stepper.close_connection()
    
        