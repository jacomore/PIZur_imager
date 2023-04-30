import numpy as np 

class OutputProcessor():

    def __init__(self,filename,scan_pars,daq_pars):
        """
        Initialize an OutputProcessor object with the given filename, scan parameters, and DAQ parameters.

        Args:
        - filename (str): the name of the file containing the output data
        - scan_pars (dict): a dictionary containing the scan parameters
        - daq_pars (dict): a dictionary containing the DAQ parameters

        Attributes:
        - scan_pars (dict): a dictionary containing the scan parameters
        - filename (str): the name of the file containing the output data
        - daq_pars (dict): a dictionary containing the DAQ parameters
        - N_rows (int): the number of rows in the DAQ data
        - N_cols (int): the number of columns in the DAQ data
        """
        self.scan_pars = scan_pars
        self.filename = filename
        self.N_rows = daq_pars["daq_rows"]
        self.N_cols = daq_pars["daq_columns"]

    def get_raw_data(self):
        """
        Read raw data from the file and return the third column, containing the values of the measured signal.

        Returns:
        - raw_data (ndarray): a NumPy array containing the third column of the input file
        """
        raw_data = np.genfromtxt(self.filename,skip_header = 1, delimiter = ";")
        return raw_data[:,2] # third column contains all the data in a column     
    
    def evaluate_averaged_data(self,raw_data): 
        """
        Average the input data in case of a 1D discrete scan.

        Args:
        - raw_data (ndarray): a NumPy array containing the raw data

        Returns:
        - avg_data (ndarray): a NumPy array containing the averaged data
        """
        avg_data = np.empty(self.N_rows)
        for row in range(self.N_rows):
            avg_data[row] = np.mean(raw_data[row*self.N_cols:(row + 1)*self.N_cols])
        return avg_data
    
    def evaluate_target_positions(self,scanedges,stepsize):
        """
        Evaluate the partition of the target points for a 1D scan.

        Args:
        - scanedges (list): a list containing the start and end positions of the scan
        - stepsize (float): the step size of the scan

        Returns:
        - targets (ndarray): a NumPy array containing the target positions
        """
        # calculate targets points
        Npoints = int(abs((scanedges[1]-scanedges[0]))/stepsize) + 1
        return np.linspace(scanedges[0],scanedges[1],Npoints,endpoint=  True)

    def save_data_file(self,targets,avg_data):         
        """
        Save the cleaned 1D data to a file.

        Args:
        - targets (ndarray): a NumPy array containing the target positions
        - avg_data (ndarray): a NumPy array containing the averaged data
        """
        out_name = "cleaned_1D_data.txt"
        out_file = np.column_stack((targets,avg_data))
        np.savetxt(out_name, out_file, fmt = "%10.6f", delimiter = ",")

    def save_processed_data(self):
        """
        Process the 1D data and save it to a file.
        """
        # get targets position
        scanedges = self.scan_pars["scan_edges"]
        stepsize = self.scan_pars["stepsize"]
        targets = self.evaluate_target_positions(scanedges,stepsize)  
        # get out_data
        raw_data = self.get_raw_data()
        if (self.scan_pars["type"] == "discrete"):
            out_data = self.evaluate_averaged_data(raw_data, )
        else: 
            out_data = raw_data
        # save data
        self.save_data_file(targets,out_data)

            
        
               
        
        


    

