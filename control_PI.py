from pipython import GCSDevice,pitools, GCS2Commands

# declaring class for new exception
class InvalidPosInput(Exception):
    "Raised when the input value is out of range"
    pass

# check input is correct 
def pos_in_range(pos,rangemin,rangemax):
    if pos <= rangemin or  pos >= rangemax:
        raise InvalidPosInput


def move_to_ref(pidevice,REFMODES):
    """move the stage towards the reference point"""
    if REFMODES == 'FNL':
        pidevice.FNL()
    elif REFMODES == 'FPL':
        pidevice.FPL()
    pitools.waitontarget(pidevice)
    print("Stage: {}".format(GCS2Commands.qCST(pidevice)['1']),"successfully referenced")


CONTROLLERNAME = 'C-663'
STAGES = 'L-406.40SD00'  # connect stages to axes
#REFMODES = 'FPL'
REFMODES = 'FNL'
DESTINATION = 1 # mm

with GCSDevice(devname = CONTROLLERNAME) as pidevice: 
    # return list of string with the found devices
    devices = pidevice.EnumerateUSB(mask=CONTROLLERNAME)
    # check that devices is not empty        
    if not devices: 
       raise Exception("There are no connected devices! Please, connect at least one device.")

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
    
    # move towards REFMODE and wait until stage is ready on target
    move_to_ref(pidevice,REFMODES)
    
    # return values of the minimum and maximum position of the travel range of axis
    rangemin = list(pidevice.qTMN().values())
    rangemax = list(pidevice.qTMX().values())

    # check entries for destination
    try:
        is_valid = pos_in_range(DESTINATION,rangemin[0],rangemax[0])
    except ValueError:
        print("That was no valid number!")
    except TypeError:
        print("That was no valid type!")
    except InvalidPosInput:
        print("Desired destination is out of range!")
        

    
    


