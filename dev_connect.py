from pipython import GCSDevice,pitools
import warnings

CONTROLLERNAME = 'C-663'
STAGES = 'L-406.40SD00'  # connect stages to axes
#REFMODES = 'FPL'
REFMODES = ('FNL')

while True:
    try:
        start = int(input("Please, input the starting point: "))
        end = int(input("Please, input the ending point: "))
        step = int(input("Please, input the step of the scan"))
        break
    except ValueError:
        print("Oops!  That was no valid number.  Try again...")

def main():
    """Connect controller and stage and display messages if successful."""
    with GCSDevice(devname = CONTROLLERNAME) as pidevice: 
        
        # return list of string with the found devices
        devices = pidevice.EnumerateUSB(mask=CONTROLLERNAME)

        # check that devices is not empty        
        if not devices: 
            with warnings.catch_warnings():
                warnings.simplefilter('error',category=Warning)
                warnings.warn("There are no connected devices! Please, connect at least one device.")

        # printout found devices
        for i, device in enumerate(devices):
            print('Number ---- Device')
            print('{}      ----  {}'.format(i,device))

        # read the selected device
        item = int(input('Input the index of the device to connect:'))
        pidevice.ConnectUSB(devices[item])
        print('connected: {}'.format(pidevice.qIDN().strip()))

        # initialise the controller and the stages
        pitools.startup(pidevice, stages = STAGES, refmodes = REFMODES)

        # return values of the minimum and maximum position of the travel range of axis
        rangemin = list(pidevice.qTMN().values())
        rangemax = list(pidevice.qTMX().values())

        if start < rangemin:
            with warnings.catch_warnings():
                warnings.simplefilter('error',category=Warning)
                warnings.warn("Input")



if __name__ == '__main__':
    # To see what is going on in the background you can remove the following
    # two hashtags. Then debug messages are shown. This can be helpful if
    # there are any issues.

    #import logging
    #logging.basicConfig(level=logging.DEBUG)

    main()