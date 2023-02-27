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
    im.set(animated = True,clim = (0,AMP),cmap = 'magma', interpolation = None)
    return im,

def update1D(data):
    """Update frame for plotting"""
    ydata.append(data[0])
    xdata.append(data[1])
    ln.set_data(xdata,ydata)
    return ln,

def update2D(data):
    out_val = np.empty(())
    idx = data[1]
    if idx % 2 == 0:
        linedat = data[0][0]
    else:
        linedat = np.flip(data[0][0])
    matrix[idx,:] = linedat
    im.set_data(matrix)
    return im,

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
        scanner = Scan_2D()
        scanner.execute_continous_2D_scan()
        fig, ax = plt.subplots()
        X_MIN , X_MAX = 0,4
        Y_MIN , Y_MAX = 0,11
        DIMX =  111
        DIMY = 200
        AMP = 3
        all_matrix = []
        matrix = np.zeros((DIMX,DIMY))
        im = plt.imshow(matrix)
        ani = FuncAnimation(fig, update2D, frames = scanner.execute_continous_2D_scan(), init_func = init2D, interval = 100,blit=True,cache_frame_data = True)
        plt.show()
        
