class InputValidator:
    """
    A class that validates the input parameters for a scanning process.

    Attributes:
        type (str): The type of the scanning process. Can be "continuous" or "discrete".
        scan_edges (tuple): The starting and ending positions of the scan in mm.
        stepsize (float): The size of the step between two consecutive scan positions in mm.
        velocity (float): The velocity of the scanner in mm/s.
        acceleration (float): The acceleration of the scanner in mm/s^2.

    Methods:
        validate_type: Validates the type of the scanning process.
        validate_scan_edges: Validates the scan edges.
        validate_stepsize: Validates the step size of the scanning process.
        validate_velocity: Validates the velocity of the scanner.
        validate_acceleration: Validates the acceleration of the scanner.
        validate: Validates all the input parameters.
    """
    def __init__(self, scan_pars):
        """
        Initializes the InputValidator class.

        Args:
            scan_pars (dict): A dictionary containing the input parameters for the scanning process.
                It must contain the following keys:
                    "type" (str): type of the scan, either "continuous" or "discrete".
                    "scan_edges" (list): a list containing the starting and final points of the scan.
                    "stepsize" (float): the step size between scan points.
                    "velocity" (float): the velocity of the scan motion in mm/s.
                    "acceleration" (float): the acceleration of the scan motion in mm/s^2.
        """
        self.type = scan_pars["type"]
        self.scan_edges = scan_pars["scan_edges"]
        self.stepsize = scan_pars["stepsize"]
        self.velocity = scan_pars["velocity"]
        self.acceleration = scan_pars["acceleration"]
        
    def validate_type(self):
        """
        Validates the type of the scanning process.

        Raises:
            ValueError: If the type is not "continuous" or "discrete".
        """
        if not (self.type == "continuous" or self.type == "discrete"):
            print("Invalid input: type must be either continuous or discrete.")
            raise ValueError
            
    def validate_scan_edges(self):
        """
        Validates the scan edges.

        Raises:
            ValueError: If the scan edges are out of range [0, 102].
        """
        if ((self.scan_edges[0] < 0.) | (self.scan_edges[0] > 102.)):
            print("Invalid input: first scan edge if out of range [0,102].")
            raise ValueError
        if ((self.scan_edges[1] < 0.) | (self.scan_edges[1] > 102.)):
            print("Invalid input: first scan edge if out of range [0,102].")
            raise ValueError
            
    def validate_stepsize(self):
        """
        Validates the step size of the scanning process.

        Raises:
            ValueError: If the step size is out of range [0.0005, 102], or the starting point plus step size are
                        out of range.
        """
        if ((self.stepsize < 0.5e-3) | (self.stepsize >= 102)):
            print("Invalid input: stepsize is out of range [0.0005,102] .")
            raise ValueError
        if (self.scan_edges[0]<self.scan_edges[1]):
            if (self.stepsize + self.scan_edges[0] > 102):
                print("Invalid input: first scan edge plus stepsize is of range.")
                raise ValueError
        elif (self.scan_edges[0] > self.scan_edges[1]):
            if (self.scan_edges[0] - self.stepsize < 0):
                print("Invalid input: first scan edge plus stepsize is of range.")
                raise ValueError
        else:
            print("Invalid input: the scan edges coincide.")
            raise ValueError
            
    def validate_velocity(self):
        """
        Validates the velocity attribute to ensure that it is within the range [0,10] mm/s.

        Raises:
            ValueError: If the velocity value is out of range [0,10] mm/s.
        """
        if ((self.velocity < 0) | (self.velocity > 10)):
            print("Invalid input: velocity value is out of range [0,10] mm/s.")
            raise ValueError
            
    def validate_acceleration(self):
        """
        Validates the acceleration attribute to ensure that it is within the range [0,20] mm/s^2.

        Raises:
            ValueError: If the acceleration value is out of range [0,20] mm/s^2.
        """
        if ((self.acceleration < 0) | (self.acceleration > 20)):
            print("Invalid input: acceleration value is out of range [0,20] mm/s^2.")
            raise ValueError
    
    def validate(self):
        """
        Calls the individual validation methods to validate all the scan parameters.
        If all the parameters pass the validation, it returns True.
        
        Returns:
            bool: True, if all the scan parameters pass the validation.
        Raises:
            ValueError: If any of the scan parameters fail the validation.
        """
        self.validate_type()
        self.validate_scan_edges()
        self.validate_stepsize()
        self.validate_velocity()
        self.validate_acceleration()
        return True
