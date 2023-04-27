from PI_commands import Stepper
from pipython import pitools,GCS2Commands

class TestStepper:
    stepper = Stepper('C-663', 'L-406.40SD00')

    def test_connect_to_dev(self):
        self.stepper.connect_pidevice()
        assert self.stepper.pidevice.IsConnected()

    def test_usb_return_list(self):
        assert isinstance(self.stepper.usb_plugged_devices(), list)
   
    def test_connect_axis(self):
        assert pitools.getaxeslist(self.stepper.pidevice, axes=None) == ['1']
    
    def test_reference_motion(self):
        self.stepper.move_stage_to_ref('FNL')
        assert self.stepper.get_curr_pos() == self.stepper.axis_edges()[0]
    
    
    #def test_pos_is_float(self):
    #    pos = self.stepper.get_curr_pos()
    #    assert isinstance(pos, float)
 
    def test_velocity_is_set(self):
        self.stepper.set_velocity(10)
        assert GCS2Commands.qVEL(self.stepper.pidevice)['1'] == 10
       
    #def test_target_is_reached(self):
    #    self.stepper.move_stage_to_target(10)
    #    assert self.stepper.get_curr_pos() == 10
    
    def test_trigger_is_set(self):
        self.stepper.configure_out_trigger(6)
        assert self.stepper.pidevice.qCTO(1, 3)[1][3] == '6'
    