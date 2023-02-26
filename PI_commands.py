from pipython import GCSDevice, pitools, GCS2Commands


class Stepper:
    """Represents an axis connected to a PI controller.

    This class provides methods for connecting to and controlling the axis, 
    including referencing the stage to a known position, moving the stage, 
    querying the position, and configuring the output trigger.

    Parameters
    ----------
    controller_ID : str
        The ID of the PI controller to connect to.
    axis_ID : str
        The ID of the axis to control.

    Attributes
    ----------
    pidevice : GCSDevice
        The underlying PI device object.
    controller_ID : str
        The ID of the PI controller this axis is connected to.
    axis_ID : str
        The ID of this axis.
        
    Methods
    -------
    USB_plugged_device()
        Returns a list of the devices plugged through USB.
    connect_pidevice()
        Selects and connects the master device.
    move_stage_to_ref(refmode)
        Moves the selected controller towards reference position.
    axis_edges()
        Returns the values of the edges of the axis, which define the scannable range.
    configure_out_trig(trigger_type)
        Configures and sets the output trigger for a given axis.

    """

    def __init__(self, controller_id, axis_id):
        """Initializes the StepperChain class.

        Parameters:
        ----------
        controller_id (str): The ID of the controller.
        axis_id (int): The ID of the axis.
        """
        self.controller_id = controller_id
        self.pidevice = GCSDevice(devname=self.controller_id)
        self.axis_id = axis_id
    
    def usb_plugged_devices(self):
        """Returns a list with the devices plugged through USB."""
        return self.pidevice.EnumerateUSB(mask=self.controller_id)
    
    def connect_pidevice(self):
        """I/O interface for selecting and connecting the master device."""
        devices = self.usb_plugged_devices()
        if not devices:
            raise Exception("There are no plugged devices! Please connect at least one device.")
        for i, device in enumerate(devices):
            print('Number ---- Device')
            print(f'{i}      ----  {device}')
        # I/O for device selection
        item = int(input('Input the index of the device to connect: '))
        self.pidevice.ConnectUSB(devices[item])
        pitools.startup(self.pidevice, self.axis_id)
        
    def move_stage_to_ref(self, refmode):
        """Moves the selected controller towards the reference position.
        
        Parameters
        ----------
        refmode : str
            String defining the referencing position.
        """
        if refmode == 'FNL':
            print("Moving stage towards negative edge...")
            self.pidevice.FNL()
        elif refmode == 'FPL':
            print("Moving stage towards positive edge...")
            self.pidevice.FPL()
        pitools.waitontarget(self.pidevice)
        print(f"Stage: {GCS2Commands.qCST(self.pidevice)['1']} successfully referenced.")
            
    def axis_edges(self):
        """Returns the values of the edges of the axis, which define the scannable range."""
        neg_edge = list(self.pidevice.qTMN().values())
        pos_edge = list(self.pidevice.qTMX().values())
        return [neg_edge[0], pos_edge[0]]
    
    def get_curr_pos(self):
        """Returns the current position of the axis"""
        return self.pidevice.qPOS(self.pidevice)['1']

    def configure_out_trigger(self, trigger_type):
        """Configures and sets the output trigger for a given axis.
        
        Parameters
        ----------
        trigger_type : int
            Type of trigger to be output (6 == in Motion, 1 = Line trigger).
        """
        self.pidevice.CTO(1, 2, 1)
        self.pidevice.CTO(1, 3, trigger_type)
        # enable trigger output with the configuration defined above
        self.pidevice.TRO(1, True)
        
        
class StepperChain:
    """Handles the connection with two pidevices, making use of the Stepper class
    to control a USB daisy chain of two devices.

    Attributes
    ----------
    controller_id : str
        The ID of the controller.
    axis_id : int
        The ID of the axis.

    Methods
    -------
    connect_daisy(dev_indices) 
        Connects master and servo to form a daisy chain.
    reference_both_stages(ref_modes)
        References both stages.
    configure_both_trig(trigger_types)
        Configures the output trigger modes of the two devices.
    """

    def __init__(self, controller_id: str, axis_id: int):
        """Initializes the StepperChain class.

        Parameters:
        controller_id (str): The ID of the controller.
        axis_id (int): The ID of the axis.
        """
        self.controller_id = controller_id
        self.axis_id = axis_id
        self.master = Stepper(controller_id, axis_id)
        self.servo = Stepper(controller_id, axis_id)

    def connect_daisy(self, dev_indices) -> None:
        """Connects master and servo to form a daisy chain.

        Parameters:
        dev_indices (List[int]): List of two integer numbers defining the connection
            of the two devices (1 = master, 2 = Servo).
        """
        devices = self.master.USB_plugged_device()
        self.master.pidevice.OpenUSBDaisyChain(description=devices[0])
        daisy_chain_id = self.master.pidevice.dcid
        self.master.pidevice.ConnectDaisyChainDevice(dev_indices[0], daisy_chain_id)
        pitools.startup(self.master.pidevice, self.master.axis_ID)
        self.servo.pidevice.ConnectDaisyChainDevice(dev_indices[1], daisy_chain_id)
        pitools.startup(self.servo.pidevice, self.master.axis_ID)

    def reference_both_stages(self, ref_modes) -> None:
        """References both stages.

        Parameters:
        ref_modes (List[str]): List of two strings defining the referencing modes.
        """
        self.master.move_stage_to_ref(ref_modes[0])
        self.servo.move_stage_to_ref(ref_modes[1])    
    
    def configure_both_trig(self, trigger_types) -> None:
        """Configures the output trigger modes of the two devices.

        Parameters:
        trigger_types (List[int]): List of integers defining the types of trigger to be output
            (6 == in Motion, 1 = Line trigger); first element is associated with master,
            second with servo.
        """
        self.master.configure_out_trig(trigger_types[0])
        self.servo.configure_out_trig(trigger_types[1])