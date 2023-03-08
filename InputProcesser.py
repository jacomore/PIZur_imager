import json
import numpy as np

class InputProcessor():
    def __init__(self,scan_pars,sampling_rate):
        self.scan_pars = scan_pars
        self.s_rate = sampling_rate
    

    def process_1d_input(self):
        
        scan_edges = self.scan_pars["scan_edges"]
        stepsize = self.scan_pars["stepsize"]
        acc = self.scan_pars["acceleration"]
        vel = self.scan_pars["velocity"]
        delta = abs(scan_edges[1]-scan_edges[0])

        if self.scan_pars["type"] == "continous":
            
            N_cols = delta/stepsize + 1
            N_rows = 1
            duration = self.duration_calculator(self,acc,delta,vel)
            return N_cols, N_rows, duration
        else:

            N_rows = delta/stepsize + 1
            duration = 0.05
            N_cols = duration * self.s_rate
            return N_cols, N_rows, duration
    

    def process_2d_input(self):
       
        scan_edges = self.scan_pars["scan_edges"]
        stepsize = self.scan_pars["stepsize"]
        
        srv_scan_edges = self.scan_pars["scan_edges"]
        srv_stepsize = self.scan_pars["stepsize"]
        
        acc = self.scan_pars["acceleration"]
        vel = self.scan_pars["velocity"]
        
        delta =  abs(scan_edges[1]-scan_edges[0])
        srv_delta = abs(srv_scan_edges[1]-srv_scan_edges[0])


        if self.scan_pars["type"] == "continous":
            if self.scan_pars["main_axis"] == "master":
                N_rows = srv_delta/srv_stepsize + 1
                N_cols = delta/stepsize + 1
                duration = self.duration_calculator(acc,delta,vel)
            
            else:
                N_rows = delta/stepsize + 1
                N_cols = srv_delta/srv_stepsize + 1
                duration = self.duration_calculator(acc,srv_delta,vel)

        else:
            N_rows = (delta/stepsize + 1)*(srv_delta/stepsize + 1)
            duration = 0.05
            N_cols = duration* self.s_rate 

        return N_cols,N_rows,duration


    def duration_calculator(self,acc,delta,vel):
            if (np.sqrt(acc*delta)<vel):
                duration = vel/acc + delta/vel
            else:
                duration = np.sqrt(delta/acc)
            return duration

            
        

