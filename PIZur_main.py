from InputProcessor import InputProcessor
from OutputProcessor import OutputProcessor
import json

s_freq = 1.67e3 # 1.67 kHz
openPars = open('input_dicts.json')
inpars = json.load(openPars)
scan_pars = inpars["scan_pars"]

InP = InputProcessor(scan_pars,s_freq)
daq_pars = InP.process_1d_input()
print(daq_pars)
OutP = OutputProcessor(filename = "dev4910_demods_0_sample_r_avg_00000.csv",
                       scan_pars = scan_pars,
                       daq_pars = daq_pars)
OutP.process_1D_data()
