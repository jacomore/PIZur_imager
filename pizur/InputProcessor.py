import numpy as np

class InputProcessor():
    """A class to process input scan parameters and provide the correct parameters to set
    in the Zurich Lock-In API data acquisition."""
    
    def __init__(self,scan_pars):
        """
        Initialize an InputProcessor instance.

        Parameters:
        -----------
        scan_pars : dict
            A dictionary containing scan parameters, including:
                - scan_edges : list of two floats
                    The edges of the scan range.
                - stepsize : float
                    The step size for the scan.
                - acceleration : float
                    The acceleration of moving stage scans.
                - velocity : float
                    The velocity of the moving stage scans.
                - sampling_frequency : float
                    The sampling frequency used for discrete scans.
                - type : str
                    The type of scan, either 'continuous' or 'discrete'.
        delta : float
            a float containing the absolute value of the distance between the scan edges.
        """
        self.scan_edges = scan_pars["scan_edges"]
        self.stepsize = scan_pars["stepsize"]
        self.acc = scan_pars["acceleration"]
        self.vel = scan_pars["velocity"]
        self.sampl_freq = scan_pars["sampling_freq"]
        self.type = scan_pars["type"]
        self.delta = self.delta_calculator()

    
    def rows_columns_contiuous(self):
            """
            Process input data to find the number of rows and columns
            for a continuous scan with PI controller and Zurich lock-in.

            Returns:
            --------
            N_cols : int
                The number of columns for the data acquisition.
            N_rows : int
                The number of rows for the data acquisition.
            """
            N_rows = 1
            N_cols = int(np.floor(self.delta/self.stepsize)) + 1
            return N_rows, N_cols
    
    def rows_columns_discrete(self):
        """
        Process input data to find the number of rows and columns
        for a discrete scan with Pi controller and Zurich lock-in

        Returns:
        --------
        N_cols : int
            The number of columns for the data acquisition.
        N_rows : int
            The number of rows for the data acquisition.
        """
        N_rows = int(np.floor(self.delta/self.stepsize)) + 1
        N_cols = int(np.floor(0.05*self.sampl_freq))
        return N_rows, N_cols

    def evaluate_daq_pars(self):
        """
        Process input data for a 1D scan to return the complete DAQ parameters
        that suit the scan parameters.

        Returns:
        --------
        daq_pars : dict
            A dictionary containing data acquisition parameters, including:
                - daq_columns : int
                    The number of columns for the data acquisition.
                - daq_rows : int
                    The number of rows for the data acquisition.
                - duration : float
                    The duration of the triggered data acquisition.
                - mode : str
                    The data acquisition mode; 'Exact (on-grid)' for discrete scan, 'Linear' for continuous
                - trigger type : str
                    The trigger type, always set to 'HW trigger'.
                - trigger edge : str
                    The trigger edge; 
                - holdoff : float
                    The holdoff time for the trigger
        """

        if self.type == "continuous":
            duration = self.duration_calculator()
            N_rows, N_cols = self.rows_columns_contiuous()
            mode = "linear"
            edge = "positive"
        else:
            duration = 0.05 # 50 milliseconds
            N_rows, N_cols = self.rows_columns_discrete()
            mode = "Exact (on-grid)"
            edge = "negative"
            
        daq_pars =  {
                    "daq_columns" : N_cols,
                    "daq_rows" : N_rows,
                    "duration" : duration,
                    "mode" : mode,
                    "trigger type" : "HW trigger",
                    "trigger edge" : edge,
                    "holdoff" : duration*(0.95),
                    }
        return daq_pars

    def delta_calculator(self):
        """
        Calculate the absolute value of the distance between the scan edges.

        Returns:
        --------
        delta : float
            Absolute value of the distance between scan edges.
        """
        return abs(self.scan_edges[1]-self.scan_edges[0])

    def duration_calculator(self):
        """
        Calculate the duration of the triggered data acquisition for a continuous scan.

        Parameters:
        -----------
        acc : float
            The acceleration of the moving stage scans.
        delta : float
            The distance between the scan edges.
        vel : float
            The velocity of the moving stage scans.

        Returns:
        --------
        duration : float
            The duration of the triggered data acquisition.
        """
        if (np.sqrt(self.acc*self.delta)>self.vel):
            duration = self.vel/self.acc + self.delta/self.vel
        else:
            duration = 2*np.sqrt(self.delta/self.acc)
        return duration

            
        

    