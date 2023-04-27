from PI_commands import Stepper
from InputProcessor import InputProcessor
from pipython import pitools,GCS2Commands
from math import isclose

class TestStepper:
    stepper = Stepper('C-663', 'L-406.40SD00')

    def test_connect_to_dev(self):
        self.stepper.connect_pidevice()
        assert self.stepper.pidevice.IsConnected()

    def test_usb_return_list(self):
        assert isinstance(self.stepper.usb_plugged_devices(), list)
   
    def test_connect_axis(self):
        assert pitools.getaxeslist(self.stepper.pidevice, axes=None) == ['1']
    
    def test_negative_reference(self):
        self.stepper.move_stage_to_ref('FNL')
        assert isclose(self.stepper.get_curr_pos()['1'],0,abs_tol=0.5e-3)

    def test_positive_reference(self):
        self.stepper.move_stage_to_ref('FPL')
        assert isclose(self.stepper.get_curr_pos()['1'],102,abs_tol=0.5e-3)

    def test_pos_is_float(self):
        pos = self.stepper.get_curr_pos()['1']
        assert isinstance(pos, float)
 
    def test_velocity_is_set(self):
        self.stepper.set_velocity(10)
        assert isclose(GCS2Commands.qVEL(self.stepper.pidevice)['1'],10,rel_tol=1e-3)
    
    def test_acceleration_is_set(self):
        self.stepper.set_acceleration(10)
        assert isclose(GCS2Commands.qACC(self.stepper.pidevice)['1'],10,rel_tol=1e-3)
       
    def test_target_is_reached(self):
        self.stepper.move_stage_to_target(10)
        assert isclose(self.stepper.get_curr_pos()['1'],10,abs_tol = 0.5e-3)
    
    def test_trigger_is_set(self):
        self.stepper.configure_out_trigger(6)
        assert self.stepper.pidevice.qCTO(1, 3)[1][3] == '6'

    def test_connection_is_closed(self):
        self.stepper.close_and_reset()
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
