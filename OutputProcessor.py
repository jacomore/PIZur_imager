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

    def get_raw_data(self):
        """read raw_data as a Numpy array and return only the third column, 
           containing the pixels in a column """
        raw_data = np.genfromtxt(self.filename,skip_header = 1, delimiter = ";")
        return raw_data[:,2] # third column contains all the data in a column     
    
    def evaluate_averaged_data(self,raw_data,N_cols,N_rows): 
        """average the input data in case of a 1D discrete scan"""
        N_cols = self.daq_pars["out_cols"]
        N_rows = self.daq_pars["out_rows"]
        avg_data = np.empty(N_rows)
        for row in range(N_rows):
            avg_data[row] = np.mean(raw_data[row*N_cols:(row + 1)*N_cols])
        return avg_data
    
    def evaluate_target_positions(self,scanedges,stepsize):
        """ Evaluate the partition of the target points for a 1D scan   
        """ 
        # calculate targets points
        Npoints = int((scanedges[1]-scanedges[0])/stepsize) + 1
        return np.linspace(scanedges[0],scanedges[1],Npoints,endpoint=  True)


#    def save_2D_data_file(self,primary,secondary,avg_data):

    def save_1D_data_file(self,targets,avg_data):
        out_name = "cleaned_1D_data.txt"
        out_file = np.column_stack((targets,avg_data))
        np.savetxt(out_name, out_file, fmt = "%10.6f", delimiter = ",")
        
        
    def save_1D_data_image(self,targets,avg_data):
        fig, ax = plt.subplots()
        ax.set_xlabel("Position [mm]", fontsize=13)
        ax.set_ylabel("Signal [a.u]", fontsize=13)
        ax.tick_params(axis='both', which='major', labelsize=13)
        ax.plot(targets, avg_data,".",color = "red",markersize=7,alpha = 1)
        fig.savefig("Output_fig.png", dpi = fig.dpi)

    def process_1D_data(self):
        # get targets position
        scanedges = self.scan_pars["scan_edges"]
        stepsize = self.scan_pars["stepsize"]
        targets = self.evaluate_target_positions(scanedges,stepsize)  
        # get out_data
        raw_data = self.get_raw_data()
        if (self.scan_pars["type"] == "discrete"):
            out_data = self.evaluate_averaged_data(raw_data)
        else: 
            out_data = raw_data
        # save data and image
        self.save_1D_data_file(targets,out_data)
        self.save_1D_data_image(targets,out_data)

    def evaluate_2D_targets(self):
        scanedges = self.scan_pars["scan_edges"]
        stepsize = self.scan_pars["stepsize"]
        targets = self.evaluate_target_positions(scanedges,stepsize)
        srv_scanedges = self.scan_pars["scan_edges_servo"]
        srv_stepsize = self.scan_pars["stepsize_servo"]
        srv_targets = self.evaluate_target_positions(srv_scanedges,srv_stepsize)
        
        if self.scan_pars["main_axis"] == "master":
            return targets, srv_targets
        else:
            return srv_targets,targets

    def save_2D_data_file(self,primary,secondary,out_data):
        """Return a tabular array with the values of the measured signal at each positions"""
        N_cols = self.daq_pars["out_cols"]
        N_rows = self.daq_pars["out_rows"]
        out_name = "cleaned_2D_data.txt"
        length_of_file = N_rows * N_cols
        out_file = np.empty(length_of_file)
        for row_idx,row in enumerate(secondary):
            row_file = np.empty(N_cols)
            out_file[row_idx*N_cols:(row_idx+1)*N_cols] =  np.column_stack((row_file,primary,out_data[row_idx*N_cols:(row_idx+1)*N_cols]))          
            
        np.savetxt(out_name, out_file, fmt = "%10.6f", delimiter = ",")

        
    def process_2D_data(self):
        primary_targets,secondary_targets = self.evaluate_2D_targets()
        raw_data = self.get_raw_data()
        if (self.scan_pars["type"]) == "discrete":
            out_data = self.evaluate_averaged_data(raw_data)
        else:
            out_data = raw_data
            
        
               
        
        


    

