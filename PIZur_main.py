from Scanner_classes import Scan1D
from multiprocess import Pipe, Process
from pipython import pitools
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import json


def execute_1D_scan(connection,dev1D,daq1D,targets):
    """ Execute the 1D scan by: (1) moving the axis on all the targets positions, 
        (2) measuring the raw_data from the Zurich lock-in (3) saving the data on read
        (4) sending data with the pipe to another process
    """

    scan_obj.evaluate_target_positions()
    scan_obj.daq1D.execute()
    scan_obj.execute_calibration_steps()
    targets = np.linspace(0,10,10)
    for target in targets: 
        if not daq1D.finished():
            raw_data = daq1D.read(True)
            dev1D.MOV(dev1D.axes,target)
            pitools.waitontarget(dev1D)
            connection.send([10,target])
            print("Position: ", target)
        else:   
            connection.send(None)
            print("Scan is finished; data are saved in:", scan_obj.complete_daq_pars["save/directory"])


def receiver(scan_obj,connection):
    """receive data from "sender.py" module. The program stops when data is received

    Args:
        connection (Connection object): is the edge of the Pipe established between plotter and sender

    Yields:
        y_data, x_data: generator that contains the appended values received from sender
    """
    print('Receiver: Running')
    index = 0
    while True:
        in_channel = connection.recv()
        if in_channel is None:
            ani.pause()
            print("Send is done: pausing animation.")
            break
        else:
            yval = scan_obj.process_raw_data(in_channel[0],index)
            print(yval)
            xval = in_channel[1]
            scan_obj.ydata.append(yval)       
            scan_obj.xdata.append(xval)
            index += 1
            yield scan_obj.ydata,scan_obj.xdata


def update(data,scan_obj):
    """Update frame for plotting"""
    scan_obj.ydata.append(data[0][0])
    scan_obj.xdata.append(data[1][0])
    scan_obj.ln.set_data(scan_obj.xdata,scan_obj.ydata)
    return scan_obj.ln,


if __name__ == "__main__":   
    # setup instruments 
    scanner = Scan1D('input_dicts.json')
    dev1D =  scanner.master.pidevice
    daq1D = scanner.lockin.daq_module
    targets = scanner.evaluate_target_positions()
    # setup connection for pipeline
    conn1 ,conn2 = Pipe(duplex = False)
    sender_process = Process(target = execute_1D_scan, name = "Sender", args = (conn2,dev1D,daq1D,targets))
    receiver_process = Process(target=receiver, name = "Receiver", args=(scanner,conn1,))
    sender_process.start()
    receiver_process.start()

    # setup two dimensional plots
    fig, ax = plt.subplots()
    xdata, ydata = [],[]
    ln, = ax.plot([],[], 'ro')
    ani = FuncAnimation(fig, update, frames = receiver(scanner,conn1), interval = 10, blit=True, fargs = (scanner,),cache_frame_data = False)

    

    