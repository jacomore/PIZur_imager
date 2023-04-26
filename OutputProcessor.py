import numpy as np 
import matplotlib.pyplot as plt 

class OutputProcessor():
    def __init__(self,filename,scan_pars,daq_pars):
        # parameters obtained in input by input_dicts
        self.scan_pars = scan_pars
        # filename that contains the output data
        self.filename = filename
        # parameters obtained by the daq
        self.daq_pars = daq_pars
        self.N_rows = daq_pars["out_rows"]
        self.N_cols = daq_pars["out_columns"]

    def get_raw_data(self):
        """read raw_data as a Numpy array and return only the third column, 
           containing the pixels in a column """
        raw_data = np.genfromtxt(self.filename,skip_header = 1, delimiter = ";")
        return raw_data[:,2] # third column contains all the data in a column     
    
    def evaluate_averaged_data(self,raw_data): 
        """average the input data in case of a 1D discrete scan"""
        avg_data = np.empty(self.N_rows)
        for row in range(self.N_rows):
            avg_data[row] = np.mean(raw_data[row*self.N_cols:(row + 1)*self.N_cols])
        return avg_data
    
    def evaluate_target_positions(self,scanedges,stepsize):
        """ Evaluate the partition of the target points for a 1D scan   
        """ 
        # calculate targets points
        Npoints = int((scanedges[1]-scanedges[0])/stepsize) + 1
        return np.linspace(scanedges[0],scanedges[1],Npoints,endpoint=  True)

    def save_1D_data_file(self,targets,avg_data):
        out_name = "cleaned_1D_data.txt"
        out_file = np.column_stack((targets,avg_data))
        np.savetxt(out_name, out_file, fmt = "%10.6f", delimiter = ",")

    def process_1D_data(self):
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
        # save data and image
        self.save_1D_data_file(targets,out_data)

            
        
               
        
        


    

