import numpy as np 
import matplotlib.pyplot as plt 

class OutputProcessor():
    def __init__(self,filename,scan_pars,daq_pars):
        # daq parameters are the data processed by InputProcessor    
        self.N_rows = daq_pars["rows"]
        self.N_cols = daq_pars["columns"]
        # parameters obtained in input by input_dicts
        self.scan_pars = scan_pars
        # filename that contains the output data
        self.filename = filename

    def get_raw_data(self):
        """read raw_data as a Numpy array and return only the third column, 
           containing the pixels in a column """
        raw_data = np.genfromtxt(self.filename,skip_header = 1, delimiter = ";")
        return raw_data[:,2] # third column contains all the data in a column     
    
    def evaluate_averaged_data(self,raw_data):
        avg_data = np.empty(self.N_rows)
        for row in range(self.N_rows):
            avg_data[row] = np.mean(raw_data[row*self.N_cols:(row + 1)*self.N_cols])
        return avg_data

    def save_1D_data_file(self,targets,avg_data):
        out_name = "averaged_data.txt"
        out_data = np.column_stack((targets,avg_data))
        np.savetxt(out_name, out_data, fmt = "%10.6f", delimiter = ",")

#    def save_2D_data_file(self,primary,secondary,avg_data):

    
    def save_1D_data_image(self,targets,avg_data):
        fig, ax = plt.subplots()
        ax.set_xlabel("Position [mm]", fontsize=13)
        ax.set_ylabel("Signal [a.u]", fontsize=13)
        ax.tick_params(axis='both', which='major', labelsize=13)
        ax.plot(targets, avg_data,".",color = "red",markersize=7,alpha = 1)
        fig.savefig("Output_fig.png", dpi = fig.dpi)
        
    def evaluate_target_positions(self,scanedges,stepsize):
        """ Evaluate the partition of the target points for a 1D scan   
        """ 
        # calculate targets points
        Npoints = int((scanedges[1]-scanedges[0])/stepsize) + 1
        return np.linspace(scanedges[0],scanedges[1],Npoints,endpoint=  True)
    
    def process_1D_data(self):
        # get targets position
        scanedges = self.scan_pars["scan_edges"]
        stepsize = self.scan_pars["stepsize"]
        targets = self.evaluate_target_positions(scanedges,stepsize)
        # evaluate avg_data
        raw_data = self.get_raw_data()
        avg_data = self.evaluate_averaged_data(raw_data)
        # save data and image
        self.save_1D_data_file(targets,avg_data)
        self.save_1D_data_image(targets,avg_data)


    def evaluate_targets_order(self):
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

   # def process_2D_data(self):
   #     primary_targets,secondary_targets = self.evaluate_targets_order()
        


    

