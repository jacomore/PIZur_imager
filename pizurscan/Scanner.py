from PI_commands import Stepper, StepperChain
import numpy as np

class LineScan:
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
        self._connect_stepper()  
        self._reference_stepper()
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


    def _connect_stepper(self):
        """
        Connects to the PI device through a user-interface I/O.
        """
        self.stepper.connect_pidevice()

    def _reference_stepper(self):
        """
        Moves stepper to the required reference position at the maximum velocity
        and acceleration. 
        """
        # Set high default values to obtain quick referencing
        max_vel = 20    # mm/s
        max_acc = 200    # mm/s^2
        self.stepper.set_velocity(max_vel)
        self.stepper.set_acceleration(max_acc)
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
        self.stepper.enable_out_trigger(trigger_type=self.PI["trig_type"])
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
            print(f"Position: {cur_pos['1']:.3f}")
        return scan_pos

    def execute_continuous_scan(self):
        """
        Executes the continuous scan by moving the axis to the last position.
        """
        self.init_scan()
        self.stepper.move_stage_to_target(self.targets[-1])


class PlaneScan:
    """
    A class for performing a 1D or 2D scan using a PI device.

    Attributes:
        PI (dict): Dictionary of PI device information.
        scan_pars (dict): Dictionary of scan parameters.
        scan_edges (list): List containing the two edges of the scan. Axis will move from the leftward to the rightward.
        stepsize (float): Step size of the scan.
        targets (numpy.ndarray): Array of target positions for the scan.
        stepper (Stepper): Stepper object for controlling the PI device.

    Methods:
        __init__(self, InPars):
            Initializes ScanPlane object with input parameters.
        __enter__(self):
            Context manager enter method.
        __exit__(self, exc_type, exc_value, traceback):
            Context manager exit method.
        _connect_stepperchain(self):
            Connects to the PI device through a user-interface I/O.
        _reference_stepperchain(self):
            Moves stepper to the required reference position at the maximum velocity and acceleration.
        evaluate_target_positions(self, scan_edges, stepsize):
            Evaluates the partition of the target points for a 1D scan.
        setup_motion_stepperchain(self):
            Stores input velocity, acceleration, and trigger type in the ROM of the device.
        init_scan_stepperchain(self):
            Disables the trigger that was previously set and moves to the first target of the scan.
        setup_motion_parameters(self):
            Sets motion parameters such as velocity, acceleration, and deceleration.
        enable_out_trigger_stepperchain(self):
            Enables the output trigger for the stepper chain based on the scan type and main axis.
        disable_out_trigger_stepperchain(self):
            Disables the output trigger for the stepper chain.
        execute_discrete_2D_scan(self):
            Executes the 2D discrete scan by moving the axes to all the target positions.
        execute_continuous_2D_scan(self):
            Executes the 2D continuous scan by moving the axes to the last position.
    """
    def __init__(self, InPars):
        """
        Initializes ScanPlane object with input parameters.

        Parameters:
        - InPars : dict
            Input parameters as a dictionary from a JSON file.
        """
        self.PI = InPars["pi"]
        self.scan_pars = InPars["scan_pars"]

        # Master parameters
        self.scan_edges = self.scan_pars["scan_edges"]
        self.stepsize = self.scan_pars["stepsize"]
        self.targets = self.evaluate_target_positions(self.scan_edges, self.stepsize)
        
        # Servo parameters
        self.servo_scan_edges = self.scan_pars["servo_scan_edges"]
        self.servo_stepsize = self.scan_pars["servo_stepsize"]
        self.servo_targets = self.evaluate_target_positions(self.servo_scan_edges, self.servo_stepsize)
        
        # Instantiate the stepper chain
        self.chain = StepperChain(self.PI["ID"], self.PI["stage_ID"])
        
    def __enter__(self):
        """
        Context manager enter method.
        Establishes the connection with the pidevice as soon as a context manager is opened
        and references the axis to either the positive or the negative edge.
        
        Returns:
        -------
        Scanner: Scanner object connected to the pidevice and referenced.
        """
        self._connect_stepperchain()  
        self._reference_stepperchain()
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
        self.chain.close_daisy_chain_connection()  # Close the connection with the pidevice

    def _connect_stepperchain(self):
        """
        Connects to the PI device through a user-interface I/O.
        """
        self.chain.connect_daisy_chain()

    def _reference_stepperchain(self):
        """
        Moves stepper to the required reference position at the maximum velocity
        and acceleration. 
        """
        # Set high default values to obtain quick referencing
        max_vel = 20    # mm/s
        self.chain.master.set_velocity(max_vel)
        self.chain.servo.set_velocity(max_vel)
        self.chain.reference_both_stages([self.PI["refmode"],self.PI["servo_refmode"]])
        
    def setup_motion_stepperchain(self):
        """
        Stores input velocity, acceleration, and trigger type in the ROM of the device.
        """
        self.enable_out_trigger_stepperchain()
        self.setup_motion_parameters()
        
    def init_scan_stepperchain(self):
        """
        Disables the trigger that was previously set and moves to the first target of the scan.
        """
        self.disable_out_trigger_stepperchain()
        self.chain.master.move_stage_to_target(self.targets[0])
        self.chain.servo.move_stage_to_target(self.servo_targets[0])
        self.setup_motion_stepperchain()
        
    def setup_motion_parameters(self):  
        """
        Sets motion parameters such as velocity, acceleration, and deceleration.
        """
        self.chain.master.set_velocity(self.scan_pars["velocity"])
        self.chain.servo.set_velocity(self.scan_pars["servo_velocity"]) # 10 mm/s is the standard velocity of the controller
        self.chain.master.set_acceleration(self.scan_pars["acceleration"])
        self.chain.servo.set_acceleration(self.scan_pars["servo_acceleration"])
        self.chain.master.set_deceleration(self.scan_pars["acceleration"])
        self.chain.servo.set_deceleration(self.scan_pars["servo_acceleration"])
        
    def evaluate_target_positions(self, scanedges, stepsize):
        """
        Evaluate the partition of the target points for a 1D scan.

        Parameters:
        - scanedges : list
            List containing the two edges of the scan.
        - stepsize : float
            Step size of the scan.

        Returns:
        -------
        numpy.ndarray:
            Array of target positions for the scan.
        """ 
        # calculate targets points
        Npoints = int((scanedges[1] - scanedges[0]) / stepsize) + 1
        return np.linspace(scanedges[0], scanedges[1], Npoints, endpoint=True)
                   
    def enable_out_trigger_stepperchain(self):
        """
        Depending on the type of scan and the main axis, set the trigger output for the controllers.
        """
        if self.scan_pars["type"] == "continuous":
            if self.scan_pars["main_axis"] == "master":
                self.chain.master.enable_out_trigger(trigger_type=6)
            elif self.scan_pars["main_axis"] == "servo":
                self.chain.servo.enable_out_trigger(trigger_type=6)
        elif self.scan_pars["type"] == "discrete":
            self.chain.master.enable_out_trigger(trigger_type=6)
            self.chain.servo.enable_out_trigger(trigger_type=6)
    
    def disable_out_trigger_stepperchain(self):
        """
        Disables the output trigger for the stepper chain.
        """
        self.chain.master.disable_out_trigger(trigger_type=6)
        self.chain.servo.disable_out_trigger(trigger_type=6)
    
    def execute_discrete_2D_scan(self):
        """
        Executes the 2D discrete scan by moving the axes to all the target positions.
        """
        self.init_scan_stepperchain()   
        if self.scan_pars["main_axis"] == "master":
            for idx_row, row in enumerate(self.servo_targets):
                self.chain.servo.move_stage_to_target(row)
                if idx_row % 2 == 0:
                    for col in self.targets:
                        self.chain.master.move_stage_to_target(col)
                else:
                    for col in self.targets[::-1]:
                        self.chain.master.move_stage_to_target(col)                        

        elif self.scan_pars["main_axis"] == "servo":
            for idx_col, col in enumerate(self.targets):
                self.chain.master.move_stage_to_target(col) 
                if idx_col % 2 == 0:
                    for row in self.servo_targets:
                        self.chain.servo.move_stage_to_target(row)    
                else:
                    for row in self.servo_targets[::-1]:
                        self.chain.servo.move_stage_to_target(row)                 
                
    def execute_continuous_2D_scan(self):
        """
        Executes the 2D continuous scan by moving the axes to the last position.
        """
        self.init_scan_stepperchain()           
        if self.scan_pars["main_axis"] == "master":
            for row_idx, row in enumerate(self.servo_targets):
                self.chain.servo.move_stage_to_target(row)           
                if row_idx % 2 == 0:
                    self.chain.master.move_stage_to_target(self.targets[-1])
                else:
                    self.chain.master.move_stage_to_target(self.targets[0])

        elif self.scan_pars["main_axis"] == "servo":
            for col_idx, col in enumerate(self.targets):
                self.chain.master.move_stage_to_target(col)               
                if col_idx % 2 == 0:
                    self.chain.servo.move_stage_to_target(self.servo_targets[-1])
                else:
                    self.chain.servo.move_stage_to_target(self.servo_targets[0])