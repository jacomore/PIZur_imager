from pipython import GCSDevice,pitools, GCS2Commands
import numpy as np


class Stepper:
    """Handle one connection with the PI controller and associated axis. 
       Stage has its servo motor switched-on and is referenced towards reference"""
    
    def __init__(self, controller_ID, axis_ID):
        self.controller_ID = controller_ID
        self.pidevice = GCSDevice(devname = self.controller_ID)
        self.axis_ID = axis_ID
    
    def USB_plugged_device(self):
        """return a list with the devices plugged through USB"""
        return self.pidevice.EnumerateUSB(mask = self.controller_ID) 
    
    def connect_pidevice(self):
        """I/O interface for selecting and connecting the master device 
        """
        devices = self.USB_plugged_device()
        if not devices: 
            raise Exception("There are no plugged devices! Please, connect at least one device.")
        for i, device in enumerate(devices):
            print('Number ---- Device')
            print('{}      ----  {}'.format(i,device))
        # I/O for device selection
        item = int(input('Input the index of the device to connect:'))
        self.pidevice.ConnectUSB(devices[item])
        pitools.startup(self.pidevice, self.axis_ID)
        
    def move_stage_to_ref(self,refmode):
        """Move the selected controller towards reference position
        
        Parameters
        -----
        refmode: str
        string defining the referencing position
        """
        if refmode == 'FNL':
            print("Moving stage towards negative edge...")
            self.pidevice.FNL()
        elif refmode == 'FPL':
            print("Moving stage towards positive edge...")
            self.pidevice.FPL()
        pitools.waitontarget(self.pidevice)
        print("Stage: {}".format(GCS2Commands.qCST(self.pidevice)['1']),"successfully referenced")
            
    def find_axis_edges(self):
        """Returns the values of the edges of the axis, which define the scannable range"
        """
        neg_edge = list(self.pidevice.qTMN().values())
        pos_edge = list(self.pidevice.qTMX().values())
        return neg_edge[0],pos_edge[0]

    def configure_out_trig(self,type):
        """
        Configures and sets the output trigger for a given axis

        Parameters
        type: int
            type of trigger to be output (6 ==  in Motion, 1 = Line trigger)

        Returns
        -------
        None
        """
        self.pidevice.CTO(1,2,1)
        self.pidevice.CTO(1,3,type)
        # enable trigger output with the configuration defined above
        self.pidevice.TRO(1,True)
        
class StepperChain():
    """Handle the connection with two pidevices, making use of the Stepper class 
       to control an USB daisy chain of two devices.   
    """
    # assuming that the controllers and the axes have equal serial number !!
    def __init__(self,controller_ID,axis_ID):
        self.controller_ID = controller_ID      
        self.axis_ID = axis_ID
        # create two instances of the Stepper class (one for each controller)
        self.master = Stepper(controller_ID,axis_ID)
        self.servo = Stepper(controller_ID,axis_ID)
    
    def connect_daisy(self,dev_indeces):
        """Connect master and servo to form a daisy chain 
        
        Parameters
        -------
        dev_indeces : list
        list of two integer numbers defining the connection of the two devices (1 = master, 2 = Servo)
        """
        devices = self.master.USB_plugged_device()
        self.master.pidevice.OpenUSBDaisyChain(description = devices[0])
        daisychainid = self.master.pidevice.dcid
        self.master.pidevice.ConnectDaisyChainDevice(dev_indeces[0],daisychainid)
        pitools.startup(self.master.pidevice,self.master.axis_ID)
        self.servo.pidevice.ConnectDaisyChainDevice(dev_indeces[1],daisychainid)
        pitools.startup(self.servo.pidevice,self.master.axis_ID)


    def reference_both_stages(self,refmodes):
        """Connect master and servo to form a daisy chain 
        
        Parameters
        -------
        refmodes : list
        list of two strings defining the referencing modes
        """
        self.master.move_stage_to_ref(refmodes[0])
        self.servo.move_stage_to_ref(refmodes[1])
    
    def configure_both_trig(self,types):
        """Configure the output trigger modes of the two devices
        
        Parameters
        --------
        types: list
            list of int defining the types of trigger to be output (6 ==  in Motion, 1 = Line trigger)
            first element is associated with master, second with servo      
        """    
        self.master.configure_out_trig(types[0])
        self.servo.configure_out_trig(types[1])
        