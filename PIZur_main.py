from Scanner_classes import Scan_1D, Scan_2D
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np

def init():
    """Initialise the AxesImage object (image attached to an axis). 
    
    Returns:
        im, : AxesImage object that represents the image    
    """
    im.set(animated = True, clim = (0,AMPLITUDE),cmap = 'magma',interpolation = None,)
    return im,

def updatefig(InData):
    line = InData[0]
    row_index = InData[1]
    print(line)
    print(type(line))
    data[row_index,:] = line[0][:]
    im.set_data(data)
    return im,

if __name__ == '__main__':

    scanner = Scan_2D('input_dicts.json')

    fig, ax = plt.subplots()
    X_MIN , X_MAX = 0 , 499
    Y_MIN, Y_MAX = 0 , 499
    STEPX , STEPY = 0.01,0.01
    DIMX, DIMY = 500 , 500 
    AMPLITUDE = 3
    data = np.empty((DIMX,DIMY))
    im = plt.imshow(data)
    
    ani = FuncAnimation(fig, updatefig, frames = scanner.execute_2D_continous_scan,init_func=init, interval = 30, blit=True,cache_frame_data = False)
    plt.show()