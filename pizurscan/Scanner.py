from pizurscan.PI_commands import Stepper
import numpy as np

class Scanner:
    """
    A class for performing a 1D scan using a PI device.

    Attributes:
        PI (dict): Dictionary of PI device information.
        scan_pars (dict): Dictionary of scan parameters.
        scan_edges (list): List containing the two edges of the scan. Axis will move from the leftward to the rightward.
        stepsize (float): Step size of the scan.
        targets (numpy.ndarray): Array of target positions for the scan.
        stepper (Stepper): Stepper object for controlling the PI device.

    Methods:
        __init__(self, InPars):
            Initializes Scanner object with input parameters.
        __enter__(self):
            Context manager enter method.
        __exit__(self, exc_type, exc_value, traceback):
            Context manager exit method.
        __connect_stepper(self):
            Connects to the PI device through a user-interface I/O.
        __reference_stepper(self):
            Setup the 1D scan in four steps.
        evaluate_target_positions(self):
            Evaluates the partition of the target points for a 1D scan.
        setup_motion_stepper(self):
            Stores input velocity, acceleration, and trigger type in the ROM of the device.
        init_scan(self):
            Disables the trigger and moves to the first target of the scan.
        execute_discrete_scan(self):
            Executes the 1D discrete scan by moving the axis on all the target positions.
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


    def __enter__(self):
        """
        Context manager enter method.
        Establishes the connection with the pidevice as soon as a context manager is opened
        and references the axis to either the positive or the negative edge.
        
        Returns:
        -------
            Scanner: Scanner object connected to the pidevice and referenced
        """
        self.__connect_stepper()  
        self.__reference_stepper()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Context manager exit method that closes the connection with the pidevice.

        Parameters:
        ----------
        - exc_type : type
            The type of the exception raised, if any. None if no exception occurred.
        - exc_value : Exception
            The exception instance raised, if any. None if no exception occurred.
        - traceback : traceback
            The traceback object related to the exception, if any. None if no exception occurred.
        """
        self.stepper.close_connection()  # Close the connection with the pidevice
        if exc_type is not None:
            print(f"Exception type: {exc_type}")
            print(f"Exception value: {exc_value}")
            print(f"Traceback: {traceback}")

    def __connect_stepper(self):
        """
        Connects to the PI device through a user-interface I/O.
        """
        self.stepper.connect_pidevice()

    def __reference_stepper(self):
        """
        Moves stepper to the required reference position at the maximum velocity
        and acceleration. 
        """
        # Set high default values to obtain quick referencing
        self.stepper.set_velocity(10)
        self.stepper.set_acceleration(20)
        self.stepper.move_stage_to_ref(self.PI["refmode"])
        
    def evaluate_target_positions(self):
        """
        Evaluates the partition of the target points for a 1D scan.

        Returns:
        --------
        numpy.ndarray: Array of target positions.
        """
        Npoints = int(abs(self.scan_edges[1] - self.scan_edges[0]) / self.stepsize) + 1
        return np.linspace(self.scan_edges[0], self.scan_edges[1], Npoints, endpoint=True)

    def setup_motion_stepper(self):
        """
        Stores input velocity, acceleration, and trigger type in the ROM of the device.
        """
        self.stepper.activate_out_trigger(trigger_type=self.PI["trig_type"])
        self.stepper.set_velocity(self.scan_pars["velocity"])
        self.stepper.set_acceleration(self.scan_pars["acceleration"])
        
    def init_scan(self):
        """
        Disables the trigger that was previously set and moves to the first target of the scan.
        """
        self.stepper.disable_out_trigger(trigger_type=self.PI["trig_type"])
        self.stepper.move_stage_to_target(self.targets[0])
        self.setup_motion_stepper()
        
    def execute_discrete_scan(self):
        """
        Executes the 1D discrete scan by moving the axis to all the target positions.

        Returns:
        --------
        scan_pos : List of scanned positions.
        """
        self.init_scan()
        scan_pos = []
        for target in self.targets:
            self.stepper.move_stage_to_target(target)        
            cur_pos = self.stepper.get_curr_pos()
            scan_pos.append(cur_pos)
        return scan_pos

    def execute_continuous_scan(self):
        """
        Executes the continuous scan by moving the axis to the last position.
        """
        self.init_scan()
        self.stepper.move_stage_to_target(self.targets[-1])
