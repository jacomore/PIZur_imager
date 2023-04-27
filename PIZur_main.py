from InputProcessor import InputProcessor
from OutputProcessor import OutputProcessor
from Scanners import Scan1D
import json

openPars = open('input_dicts.json')
inpars = json.load(openPars)
scan_pars = inpars["scan_pars"]

InP = InputProcessor(scan_pars)
daq_pars = InP.process_input()

scanner = Scan1D(inpars)
scanner.execute_continous_1D_scan()

OutP = OutputProcessor(filename = "dev4910_demods_0_sample_r_avg_00000.csv",
                       scan_pars = scan_pars,
                       daq_pars = daq_pars)
OutP.process_1D_data()
