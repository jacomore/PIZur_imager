from Scanner_classes import Scan1D
from multiprocess import Pipe, Process
from pipython import pitools
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import json

if __name__ == "__main__":   
    # setup instruments 
    scanner = Scan1D('input_dicts.json')
    
    # execute scan 1D
    scanner.execute_1D_scan()
