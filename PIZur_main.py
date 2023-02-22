from Scanner_classes import Scan1D
from multiprocess import Pipe, Process
from pipython import pitools
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import json

def update(data):
    """Update frame for plotting"""
    ydata.append(data[0][0])
    xdata.append(data[1][0])
    ln.set_data(xdata,ydata)
    return ln,


if __name__ == "__main__":   
    # setup instruments 
    scanner = Scan1D('input_dicts.json')

     # setup two dimensional plots
    fig, ax = plt.subplots()
    xdata, ydata = [],[]
    ln, = ax.plot([],[], 'ro')
    ani = FuncAnimation(fig, update, frames = scanner.execute_1D_scan(), interval = 10, blit=True, fargs = (scanner,),cache_frame_data = False)
    

    