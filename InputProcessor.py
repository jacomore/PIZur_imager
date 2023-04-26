import numpy as np

class InputProcessor():
    """Return values to be provided to the Zurich lockin """
    def __init__(self,scan_pars,sampling_rate):
        self.scan_pars = scan_pars
        self.s_rate = sampling_rate

    def process_1d_input(self):
        """Process input data for 1D scan in order to find the number of 
           rows, columns and the duration of the triggered data acquisition of the zurich lock-in"""
        scan_edges = self.scan_pars["scan_edges"]
        stepsize = self.scan_pars["stepsize"]
        acc = self.scan_pars["acceleration"]
        vel = self.scan_pars["velocity"]
        delta = abs(scan_edges[1]-scan_edges[0])

        if self.scan_pars["type"] == "continous":
            
            N_cols = int(np.floor(delta/stepsize)) + 1
            N_rows = 1
            duration = self.duration_calculator(acc,delta,vel)
            daq_pars =  {
                        "daq_columns" : N_cols,
                        "daq_rows" : N_rows,
                        "duration" : duration,
                        "mode" : "Linear",
                        "trigger type" : "HW trigger",
                        "trigger edge" : "positive",
                        "holdoff" : duration*(0.95),
                        "out_columns" : N_cols,
                        "out_rows" : N_rows
                        }
            
        else:

            N_rows = int(np.floor(delta/stepsize)) + 1
            duration = 0.05
            N_cols = int(np.floor(duration* self.s_rate))
            daq_pars =  {
                        "daq_columns" : N_cols,
                        "daq_rows" : N_rows,
                        "duration" : duration,
                        "mode" : "Exact (on-grid)",
                        "trigger type" : "HW trigger",
                        "trigger edge" : "negative",
                        "holdoff" : duration*(0.95),
                        "out_columns" : N_cols,
                        "out_rows" : N_rows
                        }
        return daq_pars
    

    def duration_calculator(self,acc,delta,vel):
            if (np.sqrt(acc*delta)>vel):
                duration = vel/acc + delta/vel
            else:
                duration = np.sqrt(delta/acc)
            return duration

            
        

