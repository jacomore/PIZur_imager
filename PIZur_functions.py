from pipython import GCSDevice,pitools, GCS2Commands
import zhinst.utils
import numpy as np

def process_raw_data(signal_paths,raw_data,index):
    """Gets and process raw_rata and updates data value

    Parameters
    ----------
    signal_paths : list
        list of strings of the subscribed nodes
    raw_data : dict
        dictionary in which read data are stored
    print_cols : index
        index : int
        number that contains the number of step of the scan so far

    Returns
    -------
    _ : float
        value that contains the average over the columns
    """
    for i, signal_path in enumerate(signal_paths):
        for signal_burst in raw_data.get(signal_path.lower(),[]):
            # skip the first two steps (required for calibration)
            if index >= 2:
                value = signal_burst["value"][index-2,:]
                return np.mean(value)


def onedim_sender(connection,targets,daq1D,dev1D):
    """ execute 1D scan and send the raw data to another process"""
    for index,position in enumerate(targets):
        # read the data as soon as the trigger is detected
        raw_data = daq1D.read(True)
        # move axis toward point of partition
        dev1D.MOV(dev1D.axes,position)
        # wait until axes are on target
        pitools.waitontarget(dev1D)
        # store actual position onto positions
        connection.send(raw_data)
