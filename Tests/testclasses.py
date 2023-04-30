from PI_commands import Stepper
from Scanners import Scan1D
from InputProcessor import InputProcessor
from pipython import pitools,GCS2Commands,GCSDevice
from math import isclose
import numpy as np 

class TestStepper:
    stepper = Stepper('C-663', 'L-406.40SD00')
    
    def test_initialization_pidevice(self):
        """Tests that when a Stepper object is initialiazed through 
        the __init__ method, the instantiation of the GCSDevice is corrected."""
        assert isinstance(self.stepper.pidevice, GCSDevice)
    
    def test_initialization_controller_axis(self):
        """Tests that when a Stepper object is initialized through
        the __init__ method, the attributes controller_id and axis_id are
        properly assigned."""
        controller = 'C-663'
        axis = 'L-406.40SD00'
        assert self.stepper.controller_id == controller
        assert self.stepper.axis_id == axis
            
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
        a connection to the controller is successfully established.
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
        the position returned by get_curr_pos is a float number."""
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
        
    def test_get_velocity(self):
        """Tests that when the Stepper object is connected, the method get_velocity
        returns the correct value of velocity"""
        velocity = self.stepper.get_velocity()
        assert isclose(GCS2Commands.qVEL(self.stepper.pidevice)['1'],velocity, rel_tol = 1e-8)
    
    def test_get_acceleration(self):
        """Tests that when the Stepper object is connected, the method get_acceleration
        returns the correct value of acceleration"""
        acceleration = self.stepper.get_acceleration()
        assert isclose(GCS2Commands.qACC(self.stepper.pidevice)['1'],acceleration, rel_tol = 1e-8)
    
    def test_velocity_is_set(self):
        """Tests that when the velocity of a connected Stepper object is set through set_velocity, 
        the velocity stored in the controller's ROM is indeed the set one."""
        self.stepper.set_velocity(15.44)
        assert isclose(self.stepper.get_velocity(),15.44,rel_tol=1e-8)
    
    def test_acceleration_is_set(self):
        """Tests that when the acceleration of a connected Stepper object is set through set_acceleration, 
        the acceleration stored in the controller's ROM is indeed the set one."""
        self.stepper.set_acceleration(12.69)
        assert isclose(self.stepper.get_acceleration(),12.69,rel_tol=1e-8)
       
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
        """Tests that when an instance of InputProcessor is created, the inizialitation of the 
        object's attributes through __init__ method is correct."""
        assert self.inputprocess.type == "discrete"
        assert isclose(self.inputprocess.scan_edges[0],0,rel_tol = 1e-8)
        assert isclose(self.inputprocess.scan_edges[1],1,rel_tol = 1e-8)
        assert isclose(self.inputprocess.stepsize,0.1,rel_tol= 1e-8)
        assert isclose(self.inputprocess.vel,1,rel_tol=1e-8)
        assert isclose(self.inputprocess.acc,1,rel_tol=1e-8)
        assert isclose(self.inputprocess.sampl_freq,100,rel_tol=1e-8)

    def test_delta_calculation(self):
        """Tests that when an InputProcessor object is instantiated, the attribute delta 
        is correctly evaluated through delta_calculator given the input scan_edges."""
        assert isclose(self.inputprocess.delta,1,rel_tol = 1e-8)
    
    def test_delta_traslation_invariant(self):
        """Tests that when an InputProcessor object is instantiated, the attribute delta 
        is invariant under rigid traslation of the scan_edges coordinates."""
        # assumes that scan_edges[1] + 10 < 102
        self.inputprocess.scan_edges[0] += 10
        self.inputprocess.scan_edges[1] += 10
        assert isclose(self.inputprocess.delta,self.inputprocess.delta_calculator(),rel_tol=1e-8)
        
    def test_duration_positive(self):
        """ Tests that when the InputProcessor object is instantiated, the computation 
        of the duration always results in a positive (>=0, if no motion is desired) number.       
        """
        assert self.inputprocess.duration_calculator() >= 0
       
    def test_duration_velocity_not_constant(self):
        """Tests that when the InputProcessor object is instantiated, the computation 
        of the duration of the motion through duration_calculator is corrected. 
        Here is covered the case in which a constant velocity is never reached, i.e, sqrt(acc*delta)<=vel         
        """
        assert isclose(self.inputprocess.duration_calculator(),2,rel_tol = 1e-8)
    
    def test_duration_velocity_constant(self):
        """Tests that when the InputProcessor object is instantiated, the computation 
        of the duration of the motion through duration_calculator is corrected. 
        Here is covered the case in which a constant velocity is reached, i.e, sqrt(acc*delta)>vel         
        """
        self.inputprocess.acc = 0.5
        assert isclose(self.inputprocess.duration_calculator(),2*np.sqrt(2),rel_tol=1e-8)

    def test_rows_continous_values(self):
        """Tests that when an InputProcessor objected is instantiated and the scan mode is set
        to continuous, the number of rows of the DAQ must be set to 1"""
        N_rows , _ = self.inputprocess.rows_columns_contiuous()
        assert N_rows == 1
        
    def test_rows_equal_cols(self):
        """Tests that when an InputProcessor object is intantiated, the number of columns obtained in 
        continuous mode is equal to the number of rows obtained in discrete mode."""
        _ , N_cols = self.inputprocess.rows_columns_contiuous()
        N_rows, _ = self.inputprocess.rows_columns_discrete()
        assert isclose(N_rows,N_cols,rel_tol = 1e-8)
        
    def test_cols_continuous_values(self):
        """Tests that when an InputProcessor objected in instantiated and the scan mode is set
        to continuous, the number of columns is given by the floor of the ratio of delta over stepsize."""
        _ , N_cols = self.inputprocess.rows_columns_contiuous()
        assert N_cols == 11
    
    def test_cols_discrete_values(self):
        """Tests that when an InputProcessor objected in instantiated and the scan mode is set
        to discrete, the number of columns of the DAQ must be set to the floor of the product
        of the sampling frequency with the characteristic time of 50 ms."""
        _ , N_cols = self.inputprocess.rows_columns_discrete()
        assert isclose(N_cols,5,1e-8)
        
    def test_rows_cols_types(self):
        """Tests that when an InputProcessor object is instantiated the types of the number of rows
        and the number of columns (calculated either in continuous or discrete mode) are integer."""
        N_rows_cont, N_cols_cont = self.inputprocess.rows_columns_contiuous()
        N_rows_disc, N_cols_disc = self.inputprocess.rows_columns_discrete()
        tup = (N_rows_cont,N_cols_cont,N_rows_disc,N_cols_disc)
        assert all(isinstance(i, int) for i in tup)

    def test_daq_pars_is_dict(self):
        """Tests that when an InputProcessor object is instantiated, the daq_pars object 
        that is constructed with the values of the DAQ is a dictionary."""
        daq_pars = self.inputprocess.evaluate_daq_pars()
        assert isinstance(daq_pars,dict)
    
    def test_daq_pars_continuous(self):
        """Tests that when an InputProcessor object is instantiated, the scan mode is set 
        to continuous and the daq_pars dictionary is built-up, the values associated
        with the keys are corrected. """
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
        """Tests that when an InputProcessor object is instantiated, the scan mode is set 
        to discrete and the daq_pars dictionary is built-up, the values associated
        with the keys are corrected. """
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
        "pi" : 	{	
            "ID":"C-663",
            "stage_ID": "L-406.40SD00",
            "refmode": "FNL",
            "trig_type":6
		    }
            }
    
    scanner = Scan1D(inPars)
    
    def test_initialization_pars(self):
        """Tests that when an instance of Scan1D is created, the inizialitation of the 
        object's attributes through __init__ method is correct."""
        assert self.scanner.PI["ID"] == "C-663"
        assert self.scanner.PI["stage_ID"] == "L-406.40SD00"
        assert self.scanner.PI["refmode"] == "FNL"
        assert self.scanner.PI["trig_type"] == 6
        assert self.scanner.scan_pars["type"] == "discrete"
        assert isclose(self.scanner.scan_pars["scan_edges"][0],0,rel_tol = 1e-8)
        assert isclose(self.scanner.scan_pars["scan_edges"][1],1,rel_tol = 1e-8)
        assert isclose(self.scanner.scan_pars["stepsize"],0.1,rel_tol = 1e-8)
        assert isclose(self.scanner.scan_pars["velocity"],1,rel_tol= 1e-8)
        assert isclose(self.scanner.scan_pars["acceleration"],1,rel_tol= 1e-8)
        assert isclose(self.scanner.scan_pars["sampling_freq"],100,rel_tol= 1e-8)
    
    def test_dimension_target_positions(self):
        """Tests that when an instance of Scan1D is created,the dimension of the 
        targets array is correct." 
        """
        N_targets = 11
        assert len(self.scanner.targets) == N_targets
        
    def test_values_target_positions(self):
        """Tests that when an instance of Scan1D is created, the first and the final 
        point of targets is correct."""
        assert isclose(self.scanner.targets[0],self.scanner.scan_edges[0],rel_tol = 1e-8)
        assert isclose(self.scanner.targets[-1],self.scanner.scan_edges[1],rel_tol = 1e-8)  # by induction is right because of linspace
    
    def test_stepper_is_instantiated(self):
        """Tests that when an instance of Scan1D is created, the instance of Stepper
        is properly instantiated throught the __init__ method."""
        assert isinstance(self.scanner.stepper,Stepper)
    
    def test_stepper_is_connected(self):
        """Tests that when an instance of Scan1D is created and connected_master is called, 
        master is properly connected to the PI controller"""
        self.scanner.connect_stepper()
        assert self.scanner.stepper.pidevice.isConnected()

    def test_vel_acc_stepper(self):
        """Tests that when an instance of Scan1D is created and stepper is connected, 
        velocity and acceleration are properly set through the method setup_motion_stepper"""
        self.scanner.setup_motion_stepper(self)
        assert isclose(self.scanner.stepper.get_velocity(),1,rel_tol = 1e-8)
        assert isclose(self.scanner.stepper.get_acceleration(),1,rel_tol = 1e-8)
        
    def test_initial_scan_position(self):
        """Tests that when an instance of Scan1D is created and init_stepper_scan is called,
        the axis is moved to the first target position."""
        self.scanner.init_stepper_scan()
        cur_pos = self.scanner.stepper.get_curr_pos()
        assert isclose(cur_pos,self.scanner.targets[0])

    def test_trigger_is_configured(self):
        """Tests that when an instance of Scan1D is created and init_1D_scan is called, 
        the output trigger is set and activated.
        """
        trig_type = self.inPars ["pi"]["trig_type"]
        assert self.scanner.stepper.pidevice.qCTO(1, 3)[1][3] == str(trig_type)
        
    def test_discrete_scan(self):
        """Tests that when an instance of Scan1D is created and execute_discrete_scan
           is performed, the covered positions are the targeted ones."""
        self.scanner.init_stepper_scan()
        cur_pos = self.scanner.execute_discrete_scan()
        assert all(abs(pos - target) <= 0.5e-3 for pos, target in zip(cur_pos, self.scanner.targets))
    
    def test_continuous_1D_scan(self):
        """Tests that when an instance of Scan1D is created and execute_continuous_scan
        is performed, the position of the stage is equal to the last target point.
        """
        self.scanner.init_stepper_scan()
        self.scanner.execute_continuous_scan()
        cur_pos = self.scanner.stepper.get_curr_pos()
        assert isclose(cur_pos,self.scanner.targets[-1])
        
        