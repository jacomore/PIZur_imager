import json
from PI_commands import Stepper
from Zhinst_commands import zhinst_lockin

class Scan1D: 
    """ Scan1D is designed to control a single PI controller and the Zurich lock-in
        with the objective of perfoming one dimensional scan along the desired axis (x or y). 
    """

    def __init__(self):
        """Unpack all the necessary parameters necessary for performing the 1D scan
           and the analysis. Parameters are then instantiated in the instruments by using
           the respective classes. Eventually, 1D is performed.
        """
        openPars = open('input_dicts.json')
        self.InPars = json.load(openPars)
        self.PI , self.zurich = self.InPars["pi"], self.InPars["zurich"]
        self.master = Stepper(self.PI["ID"],self.pi["stage_ID"]) # correct here and place only self.PI as below, more compact
        self.lockin = zhinst_lockin(self.zurich) 
        pass


        