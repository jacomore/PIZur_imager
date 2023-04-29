from PI_commands import Stepper
from Scanners import Scan1D
from InputProcessor import InputProcessor
from pipython import pitools,GCS2Commands
from math import isclose

class TestStepper:
    stepper = Stepper('C-663', 'L-406.40SD00')

    def test_usb_return_list(self):
        """
        Tests that when a Stepper object is passed to 
        usb_plugged_devices the returned object is a list.
        """
        assert isinstance(self.stepper.usb_plugged_devices(), list)
    
    def test_usb_return_notempty_list(self):
        """Test that when a Stepper object is passed to 
        usb_plugged_devices, the returned list is not empty."""
        assert self.stepper.usb_plugged_devices() != []
        
    def test_connection_is_established(self):
        """
        Tests that when a Stepper object is passed to connect_pidevice,
        a connection to the controller is succesfully established.
        """
        self.stepper.connect_pidevice()
        assert self.stepper.pidevice.IsConnected()
  
    def test_connected_axis(self):
        """
        Tests that when a Stepper object is connected, the connected axis 
        is one ('1'). C663 controller supports connection with only 
        axis at a time. 
        """
        assert pitools.getaxeslist(self.stepper.pidevice, axes=None) == ['1']
        
    def test_pos_is_float(self):
        """Tests that when the current position of a connected Stepper object is probed, 
        the position returned by get_curr_pos is indeed a float number."""
        pos = self.stepper.get_curr_pos()['1']
        assert isinstance(pos, float)
    
    def test_pos_is_in_range(self):
        """Tests that when the current position of a connected Stepper object is probed, 
        the position returned by get_curr_pos is comprised in the available range (0,102)"""
        pos = self.stepper.get_curr_pos()['1']
        assert pos >= 0.
        assert pos <= 102.
        
    def test_negative_reference(self):
        """Tests that when a connected Stepper object is referenced to the
        negative edge of the axis through move_stage_to_ref, the final position
        is indeed the negative edge (0)."""
        self.stepper.move_stage_to_ref('FNL')
        assert isclose(self.stepper.get_curr_pos()['1'],0,rel_tol=1e-8)

    def test_positive_reference(self):
        """Tests that when a connected Stepper object is referenced to the
        positive edge of the axis through move_stage_to_ref, the final position
        is indeed the positive edge (102)."""
        self.stepper.move_stage_to_ref('FPL')
        assert isclose(self.stepper.get_curr_pos()['1'],102,rel_tol=1e-8)

    def test_velocity_is_set(self):
        """Tests that when the velocity of a connected Stepper object is set through set_velocity, 
        the velocity stored in the controller's ROM is indeed the set one."""
        self.stepper.set_velocity(10)
        assert isclose(GCS2Commands.qVEL(self.stepper.pidevice)['1'],10,rel_tol=1e-8)
    
    def test_acceleration_is_set(self):
        """Tests that when the acceleration of a connected Stepper object is set through set_acceleration, 
        the acceleration stored in the controller's ROM is indeed the set one."""
        self.stepper.set_acceleration(10)
        assert isclose(GCS2Commands.qACC(self.stepper.pidevice)['1'],10,rel_tol=1e-8)
       
    def test_target_is_reached(self):
        """Tests that when the connected Stepper object is moved to a certain target through 
        move_stage_to_target, the position when the motion is completed is equal to the target."""
        self.stepper.move_stage_to_target(10)
        assert isclose(self.stepper.get_curr_pos()['1'],10,rel_tol=1e-8)
    
    def test_trigger_is_set(self):
        """Tests that when the trigger of the connected Stepper object is set through 
        configure out_trigger, the type of trigger stored in the ROM is the selected one."""
        self.stepper.configure_out_trigger(6)
        assert self.stepper.pidevice.qCTO(1, 3)[1][3] == '6'

    def test_connection_is_closed(self):
        """Tests that the connection of the Stepper object with controller is indeed closed 
        with close_connection."""
        self.stepper.close_connection()
        assert not self.stepper.pidevice.IsConnected()


class TestInputProcessor:
    scanPars = {		
			    "type": "discrete",
			    "scan_edges": [0,1],
                "stepsize" : 0.1,
			    "velocity" : 1,
		    	"acceleration" : 1,
			    "sampling_freq" : 100
		        }

    inputprocess = InputProcessor(scanPars)

    def test_initialization(self):
        assert self.inputprocess.type == "discrete"
        assert isclose(self.inputprocess.scan_edges[0],0,rel_tol = 1e-8)
        assert isclose(self.inputprocess.scan_edges[1],1,rel_tol = 1e-8)
        assert isclose(self.inputprocess.stepsize,0.1,rel_tol= 1e-8)
        assert isclose(self.inputprocess.vel,1,rel_tol=1e-8)
        assert isclose(self.inputprocess.acc,1,rel_tol=1e-8)
        assert isclose(self.inputprocess.sampl_freq,100,rel_tol=1e-8)

    def test_delta_calculation(self):
        assert isclose(self.inputprocess.delta,1,rel_tol = 1e-8)

    def test_duration_calculator(self):
        assert isclose(self.inputprocess.duration_calculator(),2,rel_tol = 1e-8)

    def test_rows_cols_continous_values(self):
        N_rows , N_cols = self.inputprocess.rows_columns_contiuous()
        assert N_rows == 1
        assert N_cols - self.inputprocess.delta/self.inputprocess.stepsize<=1

    def test_rows_cols_discrete_values(self):
        N_rows, N_cols = self.inputprocess.rows_columns_discrete()
        assert N_rows - self.inputprocess.delta/self.inputprocess.stepsize<=1
        assert N_cols/self.inputprocess.sampl_freq <= 0.05

    def test_rows_cols_types(self):
        N_rows_cont, N_cols_cont = self.inputprocess.rows_columns_contiuous()
        N_rows_disc, N_cols_disc = self.inputprocess.rows_columns_discrete()
        tup = (N_rows_cont,N_cols_cont,N_rows_disc,N_cols_disc)
        assert all(isinstance(i, int) for i in tup)

    def test_daq_pars_is_dict(self):
        daq_pars = self.inputprocess.evaluate_daq_pars()
        assert isinstance(daq_pars,dict)
    
    def test_daq_pars_continuous(self):
        self.inputprocess.type = "continuous"
        daq_pars = self.inputprocess.evaluate_daq_pars()
        N_rows, N_cols = self.inputprocess.rows_columns_contiuous()
        duration = self.inputprocess.duration_calculator()
        assert daq_pars["daq_columns"] == N_cols
        assert daq_pars["daq_rows"] == N_rows
        assert daq_pars["duration"] == duration
        assert daq_pars["mode"] == "linear"
        assert daq_pars["trigger type"] == "HW trigger"
        assert daq_pars["trigger edge"] == "positive"
        assert isclose(daq_pars["holdoff"],duration*0.95,rel_tol = 1e-8)

    def test_daq_pars_discrete(self):
        self.inputprocess.type = "discrete"
        daq_pars = self.inputprocess.evaluate_daq_pars()
        N_rows, N_cols = self.inputprocess.rows_columns_discrete()
        duration = 0.05
        assert daq_pars["daq_columns"] == N_cols
        assert daq_pars["daq_rows"] == N_rows
        assert daq_pars["duration"] == duration
        assert daq_pars["mode"] == "Exact (on-grid)"
        assert daq_pars["trigger type"] == "HW trigger"
        assert daq_pars["trigger edge"] == "negative"
        assert isclose(daq_pars["holdoff"],duration*0.95,rel_tol = 1e-8)


class TestScanners:
    inPars = {
        "scan_pars" : {		
            "type": "discrete",
            "scan_edges": [0,1],
            "stepsize" : 0.1,
            "velocity" : 1,
            "acceleration" : 1,
            "sampling_freq" : 100
            },
    "pi" : 	{	"ID":"C-663",
            "stage_ID": "L-406.40SD00",
            "refmode": "FNL"
		    }
    }
    
    scanner = Scan1D(inPars)
    
    def test_initialization_pars(self):
        assert self.scanner.PI["ID"] == "C-663"
        assert self.scanner.PI["stage_ID"] == "L-406.40SD00"
        assert self.scanner.PI["refmode"] == "FNL"
        assert self.scanner.scan_pars["type"] == "discrete"
        assert isclose(self.scanner.scan_pars["scan_edges"][0],0,rel_tol = 1e-8)
        assert isclose(self.scanner.scan_pars["scan_edges"][1],1,rel_tol = 1e-8)
        assert isclose(self.scanner.scan_pars["stepsize"],0.1,rel_tol = 1e-8)
        assert isclose(self.scanner.scan_pars["velocity"],1,rel_tol= 1e-8)
        assert isclose(self.scanner.scan_pars["acceleration"],1,rel_tol= 1e-8)
        assert isclose(self.scanner.scan_pars["sampling_freq"],100,rel_tol= 1e-8)

    def test_stepper_instantiated(self):
        assert self.scanner.master is not None
    
    def test_evaluate_target_positions(self):
        self.scanner.evaluate_target_positions()
        Npoints = int(abs(self.scanner.scan_edges[1]-self.scanner.scan_edges[0])/self.scanner.stepsize) + 1
        assert len(self.scanner.targets == Npoints)
        assert self.scanner.targets[0] == self.scanner.scan_edges[0]
        assert self.scanner.targets[-1] == self.scanner.scan_edges[1]  # by induction is right because of linspace
        
        