import numpy as np 
import matplotlib.pyplot as plt 
import json

class DataProcessor():

    def __init___(self,filename,ncols):
        # input acquisition parameters
        openPars = open('input_dicts.json')
        InPars = json.load(openPars)
        self.PI = InPars["pi"]        
        self.scan_pars = InPars["scan_pars"]

        # input raw_data
        raw_data = np.genfromtxt(filename,skip_header = 1, delimiter = ";")
        self.data = raw_data[:,2] # third column contains all the data in a column

     