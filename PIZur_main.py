from Scanner_classes import Scan1D
from multiprocessing import Pipe, Process
from pipython import pitools
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def execute_1D_scan(scan_obj,connection):
    """ Execute the 1D scan by: (1) moving the axis on all the targets positions, 
        (2) measuring the raw_data from the Zurich lock-in (3) saving the data on read
        (4) sending data with the pipe to another process
    """

    scan_obj.evaluate_target_positions()
    scan_obj.lockin.daq_module.execute()
    scan_obj.execute_calibration_steps()
    for target in scan_obj.targets: 
        if not scan_obj.lockin.daq_module.finished():
            raw_data = scan_obj.lockin.daq_module.read(True)
            scan_obj.master.pidevice.MOV(scan_obj.master.pidevice.axes,target)
            pitools.waitontarget(scan_obj.master.pidevice)
            connection.send([raw_data,target])
            print("Position: ", target)
        else:   
            connection.send(None)
            print("Scan is finished; data are saved in:", scan_obj.complete_daq_pars["save/directory"])


def receiver(scan_obj,connection):
    """receive data from "execute_1D_scan" module. The program stops when data is received

    Args:
        connection (Connection object): is the edge of the Pipe established between plotter and sender

    Yields:
        y_data, x_data: generator that contains the appended values received from execute_1D_scan
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
            xval = in_channel[1]
            ydata.append(yval)       
            xdata.append(xval)
            index += 1
            yield ydata,xdata


def update(data):
    """Update frame for plotting"""
    ydata.append(data[0][0])
    xdata.append(data[1][0])
    ln.set_data(xdata,ydata)
    return ln,


if __name__ == "__main__":   
    # setup instruments 
    scanner = Scan1D('input_dicts.json')
    # setup connection for pipeline
    conn1 ,conn2 = Pipe(duplex = False)
    sender_process = Process(target = execute_1D_scan, name = "Sender", args = (scanner,conn2,))
    receiver_process = Process(target=receiver, name = "Receiver", args=(scanner,conn1,))
    sender_process.start()
    receiver_process.start()

    # setup two dimensional plots
    fig, ax = plt.subplots()
    xdata, ydata = [],[]
    ln, = ax.plot([],[], 'ro')
    ani = FuncAnimation(fig, update, frames = receiver(scanner,conn1), interval = 10, blit=True, fargs = (scanner,),cache_frame_data = False)

    

    