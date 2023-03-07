from Scanner_classes import Scan1D, Scan_2D
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np

dim = 2

def init1D():
    ax.set_xlim(0,12)
    ax.set_ylim(0,3)
    return ln,

def init2D():
    ax.set(animated = True,clim = (0,3))


def update1D(data):
    """Update frame for plotting"""
    ydata.append(data[0])
    xdata.append(data[1])
    ln.set_data(xdata,ydata)
    return ln,

def update2D(data):
    print(len(data[0][0]))
    idx = data[1]
    if idx % 2 == 0:
        linedat = data[0][0]
    else:
        linedat = np.flip(data[0][0])
    matrix[idx,:] = linedat
    print(matrix[:,:10])
    ax.imshow(matrix, cmap = 'viridis', vmin = 0, vmax = 1,interpolation='nearest')

if __name__ == "__main__":   
    if dim ==  1:
        scanner = Scan1D             # setup one dimensional plots
        fig, ax = plt.subplots()
        xdata, ydata = [],[]
        ln, = ax.plot([],[], 'ro')
        ani = FuncAnimation(fig, update1D, frames = scanner.execute_continous_1D_scan(), interval = 1,init_func = init1D, blit=True,cache_frame_data = False)
        plt.show()
    
    else:
            # setup instruments 
            """

        fig, ax = plt.subplots()
        X_MIN , X_MAX = 0,4
        Y_MIN , Y_MAX = 0,11
        DIMX =  200
        DIMY = 200
        AMP = 3
        matrix = np.zeros((DIMX,DIMY))
        ani = FuncAnimation(fig, update2D, frames = scanner.execute_continous_2D_scan(), interval = 100)
        plt.show()
        """
            scanner = Scan_2D()
            scanner.execute_continous_2D_scan()
            
        
