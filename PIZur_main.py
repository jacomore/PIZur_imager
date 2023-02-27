from Scanner_classes import Scan1D, Scan_2D
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np

def init():
    ax.set_xlim(0,12)
    ax.set_ylim(0,3)
    return ln,


def update(data):
    """Update frame for plotting"""
    ydata.append(data[0])
    xdata.append(data[1])
    ln.set_data(xdata,ydata)
    return ln,


if __name__ == "__main__":   
    # setup instruments 
    scanner = Scan1D()

     # setup two dimensional plots
    fig, ax = plt.subplots()
    xdata, ydata = [],[]
    ln, = ax.plot([],[], 'ro')
    ani = FuncAnimation(fig, update, frames = scanner.execute_continous_1D_scan(), interval = 1,init_func = init, blit=True,cache_frame_data = False)
    plt.show()