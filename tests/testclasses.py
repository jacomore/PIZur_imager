from pizurscan.PI_commands import Stepper
from pizurscan.Scanner import Scanner
from pizurscan.InputProcessor import *
from pipython import pitools,GCS2Commands,GCSDevice
from pizurscan.OutputProcessor import *
from pizurscan.InputValidator import *
import pytest as pytest
from math import isclose
import numpy as np 

class TestStepper:
    def setup_method(self, method):
        """Setup any state tied to the execution of the given method in a class.
        `setup_method` is invoked for every test method of a class.
        in the Setup, an instance of the stepper class is created and a PI_device is connected
        """
        self.stepper = Stepper('C-663', 'L-406.40SD00')
        self.stepper.connect_pidevice()
    
    def teardown_method(self, method):
        """teardown any state that was previously setup with a setup_method
        call. In particular, it calls close_connection.
        """
        self.stepper.close_connection()
        self.stepper = None
        
    def test_initialization_controller_axis(self):
        """Tests that when a Stepper object is initialized through
        the __init__ method, the attributes controller_id and axis_id are
        properly assigned."""
        controller = 'C-663'
        axis = 'L-406.40SD00'
        # make id of controller and axis attributes
        assert self.stepper.controller_id == controller
        assert self.stepper.axis_id == axis
            
    def test_usb_return_notempty_list(self):
        """Test that when a Stepper object is passed to 
        usb_plugged_devices, the returned list is not empty."""
        assert self.stepper.usb_plugged_devices() != []
        
    def test_select_device(self):
        """Test that when select device is called on a list of devices,
        the one selected with the input is correct."""
        random_devs = ["Device1", "Device2", "Device3"]
        device = self.stepper.select_device(devices = random_devs)
        assert device in random_devs
    
    #######################
    def test_startup_USB_device(self): 
        """Tests that when the PI device with the known name is connected
        with ConnectUSB and startup, a connection is established."""    
        self.stepper.close_connection()
        dev_name = "###########"
        self.stepper.startup_USB_device()
        assert self.stepper.pidevice.IsConnected()
        
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
        self.stepper.set_velocity(5)
        assert isclose(self.stepper.get_velocity(),5,rel_tol=1e-8)
    
    def test_acceleration_is_set(self):
        """Tests that when the acceleration of a connected Stepper object is set through set_acceleration, 
        the acceleration stored in the controller's ROM is indeed the set one."""
        self.stepper.set_acceleration(5)
        assert isclose(self.stepper.get_acceleration(),5,rel_tol=1e-8)
       
    def test_target_is_reached(self):
        """Tests that when the connected Stepper object is moved to a certain target through 
        move_stage_to_target, the position when the motion is completed is equal to the target."""
        self.stepper.move_stage_to_ref('FNL')
        self.stepper.move_stage_to_target(10)
        assert isclose(self.stepper.get_curr_pos()['1'],10,rel_tol=1e-8)
    
    def test_trigger_is_enabled(self):
        """Tests that when the trigger of the connected Stepper object is set through 
        configure out_trigger, the type of trigger stored in the ROM is the selected one."""
        self.stepper.enable_out_trigger(6)
        assert self.stepper.pidevice.qCTO(1, 3)[1][3] == '6'
    
    ########################################
    def test_trigger_is_disabled(self):
        """Tests that when the trigger of the connected Stepper object is set through 
        configure out_trigger, the type of trigger stored in the ROM is the selected one."""
        self.stepper.disable_out_trigger(6)
        assert not self.stepper.pidevice.qTRO(1, 3)[1][3] 

    def test_connection_is_closed(self):
        """Tests that the connection of the Stepper object with controller is indeed closed 
        with close_connection."""
        self.stepper.close_connection()
        assert not self.stepper.pidevice.IsConnected()

class TestInputProcessor:
    def setup_method(self, method):
        """Setup any state tied to the execution of the given method in a class.
        `setup_method` is invoked for every test method of a class.
        """
        self.scanPars = {		
			    "type": "discrete",
			    "scan_edges": [0,1],
                "stepsize" : 0.1,
			    "velocity" : 1,
		    	"acceleration" : 1,
			    "sampling_freq" : 100
		        }
    
    def teardown_method(self, method):
        """teardown any state that was previously setup with a setup_method
        call. 
        """
        self.scanPars = None

    def test_delta_calculation(self):
        """Tests that when the function delta_calculator is called, it correctly evaluates
        the delta value given the input scan_edges."""
        expected_delta = 1
        calculated_delta = delta_calculator(self.scanPars["scan_edges"])
        assert isclose(calculated_delta,expected_delta,rel_tol = 1e-8)
    
    def test_delta_traslation_invariant(self):
        """Tests that when the both the scan_edges values are shifted by a constant number, 
        the delta values before and after translation calculated with delta_calculator are the same."""
        # assumes that scan_edges[1] + 10 < 102
        delta_before_traslation = delta_calculator(self.scanPars["scan_edges"])
        scan_edges = self.scanPars["scan_edges"]
        scan_edges[0] += 10
        scan_edges[1] += 10
        delta_after_translation = delta_calculator(scan_edges)
        assert isclose(delta_before_traslation,delta_after_translation,rel_tol=1e-8)
        
    def test_duration_velocity_not_constant(self):
        """Tests that when a constant velocity of the stepper is never reached, the computation 
        of the duration of the motion through duration_calculator is corrected.          
        """
        delta = delta_calculator(self.scanPars["scan_edges"])
        vel, acc = self.scanPars["velocity"], self.scanPars["acceleration"]
        duration = duration_calculator(delta,vel,acc)
        assert isclose(duration,2,rel_tol = 1e-8)
    
    def test_duration_velocity_constant(self):
        """Tests that when a constant velocity of the stepper is reached, the computation 
        of the duration of the motion through duration_calculator is corrected.          
        """
        delta = delta_calculator(self.scanPars["scan_edges"])
        vel, acc = self.scanPars["velocity"], 2
        duration = duration_calculator(delta,vel,acc)
        assert isclose(duration,2*np.sqrt(2),rel_tol=1e-8)

    def test_rows_continous_values(self):
        """Tests that when the type of scan is set to continuous, the number of rows
        that are calculated with rows_columns_continuous is correct. 
        """
        delta = delta_calculator(self.scanPars["scan_edges"])
        stepsize = self.scanPars["stepsize"]
        N_rows , _ = rows_columns_contiuous(delta,stepsize)
        assert N_rows == 1
        
    def test_cols_continuous_values(self):
        """Tests that when the type of scan is set to continuous, the number of columns
        that are calculated with rows_columns_continuous is correct. 
        """
        delta = delta_calculator(self.scanPars["scan_edges"])
        stepsize = self.scanPars["stepsize"]
        _ , N_cols = rows_columns_contiuous(delta,stepsize)
        assert N_cols == 11
        
    def test_rows_discrete_values(self):
        """Tests that when the type of scan is set to discrete, the number of rows
        that are calculated with rows_columns_discrete is correct. 
        """
        delta = delta_calculator(self.scanPars["scan_edges"])
        stepsize = self.scanPars["stepsize"]
        sampl_freq = self.scanPars["samp_freq"]
        N_rows, _ = rows_columns_discrete(delta,stepsize,sampl_freq)
        assert N_rows == 11
    
    def test_cols_discrete_values(self):
        """Tests that when the type of scan is set to discrete, the number of columns
        that are calculated with rows_columns_discrete is correct. 
        """
        delta = delta_calculator(self.scanPars["scan_edges"])
        stepsize = self.scanPars["stepsize"]
        sampl_freq = self.scanPars["samp_freq"]
        _ , N_cols = rows_columns_discrete(delta,stepsize,sampl_freq)
        assert N_cols == 5
        
    def test_rows_cols_types(self):
        """Tests that when rows and columns are calculated in discrete and continuous mode through 
        rows_columns_continuous and rows_columns_discrete, respectively, the outputted numbers are integer.""""
        delta = delta_calculator(self.scanPars["scan_edges"])
        stepsize = self.scanPars["stepsize"]
        sampl_freq = self.scanPars["samp_freq"]
        N_rows_cont, N_cols_cont = rows_columns_contiuous(delta,stepsize)
        N_rows_disc, N_cols_disc = rows_columns_discrete(delta,stepsize,sampl_freq)
        tup = (N_rows_cont,N_cols_cont,N_rows_disc,N_cols_disc)
        assert all(isinstance(i, int) for i in tup)
    
    def test_daq_pars_continuous(self):
        """ Tests that when the type of scan is set to continuous, the values of the dictionary "daq_pars" 
        calculated with the function evaluate_daq_pars are correct.
        """
        self.scanPars["type"] == "continuous"
        daq_pars = evaluate_daq_pars(self.scanPars)
    
        assert daq_pars["daq_columns"] == 11
        assert daq_pars["daq_rows"] == 1
        assert daq_pars["duration"] == 2
        assert daq_pars["mode"] == "linear"
        assert daq_pars["trigger type"] == "HW trigger"
        assert daq_pars["trigger edge"] == "positive"
        assert isclose(daq_pars["holdoff"],2*0.95,rel_tol = 1e-8)

    def test_daq_pars_discrete(self):
        """ Tests that when the type of scan is set to discrete, the values of the dictionary "daq_pars" 
        calculated with the function evaluate_daq_pars are correct.
        """
        daq_pars = evaluate_daq_pars(self.scanPars)
        duration = 0.05
        assert daq_pars["daq_columns"] == 5
        assert daq_pars["daq_rows"] == 11
        assert isclose(daq_pars["duration"],duration,rel_tol=1e-8)
        assert daq_pars["mode"] == "Exact (on-grid)"
        assert daq_pars["trigger type"] == "HW trigger"
        assert daq_pars["trigger edge"] == "negative"
        assert isclose(daq_pars["holdoff"],duration*0.95,rel_tol = 1e-8)

class TestScanners:
    def setup_method(self, method):
        """Setup any state tied to the execution of the given method in a class.
        `setup_method` is invoked for every test method of a class.
        """
        self.inPars = {
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
        self.scanner = Scanner(self.inPars)

    
    def teardown_method(self, method):
        """teardown any state that was previously setup with a setup_method
        call.
        """
        self.scanner = None
        self.inPars = None
                
    def test_initialization_pars(self):
        """Tests that when an instance of scanner is created, the inizialitation of the 
        object's attributes through __init__ method is correct."""
        assert self.scanner.PI["ID"] == "C-663"
        assert self.scanner.PI["stage_ID"] == "L-406.40SD00"
        assert self.scanner.PI["refmode"] == "FNL"
        assert self.scanner.PI["trig_type"] == 6
        assert self.scanner.scan_pars["type"] == "discrete"
        assert isclose(self.scanner.scan_pars["scan_edges"][0],0,rel_tol = 1e-8)
        assert isclose(self.scanner.scan_pars["scan_edges"][1],1,rel_tol = 1e-8)
        assert isclose(self.scanner.scan_pars["stepsize"],0.1,rel_tol = 1e-8)
        
    def test_dimension_target_positions(self):
        """Tests that when an instance of scanner is created,the dimension of the 
        targets array is correct." 
        """
        N_targets = 11
        assert len(self.scanner.targets) == N_targets
        
    def test_values_target_positions(self):
        """Tests that when an instance of scanner is created, the first and the final 
        point of targets are correct."""
        assert isclose(self.scanner.targets[0],self.scanner.scan_edges[0],rel_tol = 1e-8)
        assert isclose(self.scanner.targets[-1],self.scanner.scan_edges[1],rel_tol = 1e-8)  # by induction is right because of linspace
    
    def test_stepper_is_instantiated(self):
        """Tests that when an instance of scanner is created, the instance of Stepper
        is properly instantiated throught the __init__ method."""
        assert isinstance(self.scanner.stepper,Stepper)
    
    def test_context_manager_enter(self):
        """Tests that when an instance of scanner is created and the context manager is opened, 
        the stepper object connects to the controller and gets referenced to negative edge."""
        with self.scanner as scan:
            assert scan.stepper.pidevice.isConnected()
            assert isclose(scan.stepper.get_curr_pos()['1'],0,rel_tol=1e-8)

    def test_context_manager_exit(self):
        """Tests that when an instance of scanner is created and the context manager is opened and closed, 
        the connection is also closed"""
        with self.scanner as scan:
            pass
        assert not self.scanner.stepper.pidevice.isConnected()

    def test_discrete_scan(self):
        """Tests that when an instance of Scan1D is created and execute_discrete_scan
           is performed, the covered positions are the targeted ones."""
        with self.scanner as scan:
            cur_pos = scan.execute_discrete_scan()
        assert all(abs(pos - target) <= 0.5e-3 for pos, target in zip(cur_pos, self.scanner.targets))

class TestOutputProcessor:
    def setup_method(self, method):
        """Setup any state tied to the execution of the given method in a class.
        `setup_method` is invoked for every test method of a class.
        """
        
        self.scan_pars = {		
                        "type": "discrete",
                        "scan_edges": [0.3,0.],
                        "stepsize" : 0.001,
                        "velocity" : 1,
                        "acceleration" : 1,
                        "sampling_freq" : 100
                        }
        self.daq_pars = {
                        "daq_columns" : 100,
                        "daq_rows" : 300,
                        "duration" : 0.05,
                        "mode" : "Exact (on-grid)",
                        "trigger type" : "HW trigger",
                        "trigger edge" : "negative",
                        "holdoff" : 0.05*(0.95),
                        }   
        self.filename =  "input/dev4910_demods_0_sample_r_avg_00000.csv"  
                    
    def teardown_method(self, method):
        """teardown any state that was previously setup with a setup_method
        call.
        """
        self.scan_pars = None
        self.daq_pars = None

    def test_raw_data_values(self):
        """Tests that when when the data outputted by the Zurich lock-in are read through get_raw_data,
        the returned NumPy has the same values of the original one.
        """
        # find raw data column directly, select only non nan values
        raw_data = np.genfromtxt(self.filename,skip_header = 1, delimiter = ";")
        raw_column = raw_data[:,2]
        raw_column_not_nan = raw_column[~np.isnan(raw_column)]
        # find raw data through get_raw_data, select only non nan values
        returned_column = get_raw_data(self.filename)
        returned_column_not_nan = returned_column[~np.isnan(returned_column)]
        assert all(abs(raw - returned)/raw <= 1e-8 for raw, returned in zip(raw_column_not_nan,returned_column_not_nan))
    
    def test_dimension_averaged_subintervals_is_rows(self):
        """Tests tat when raw data are read with get_raw_data and evaluate_averaged_data is called, 
        the dimension of the returned array (with averaged subintervals) is equal to the 
        number of rows"""
        returned_column = get_raw_data(self.filename)
        avg_returned_column = evaluate_averaged_data(returned_column)
        N_rows_avg = len(avg_returned_column)
        assert self.daq_pars["daq_rows"] == N_rows_avg
        
    def test_average_data(self):
        """Tests that when raw data are read by get_raw_data and evaluate_average_data
        is called, the average of the averaged subintervals (of N_cols dimensions) is equal to the
        average of the overall raw_data. This is justified by subintervals of equal dimension
        """
        # find raw data column directly, select only non nan values
        raw_data = np.genfromtxt(self.filename,skip_header = 1, delimiter = ";")
        raw_column = raw_data[:,2]
        raw_column_not_nan = raw_column[~np.isnan(raw_column)]
        avg_raw= np.mean(raw_column_not_nan)
        # find raw data through get_raw_data, select only non nan values
        returned_column = get_raw_data(self.filename)
        returned_column_not_nan = returned_column[~np.isnan(returned_column)]        
        # average subintervals of returned_column_not_nan
        avg_returned_column = evaluate_averaged_data(returned_column_not_nan)
        # average averaged subintervals of returned_column_not_nan
        avg_avg_returned = np.mean(avg_returned_column)
        assert isclose(avg_avg_returned,avg_raw,rel_tol = 1e-8)
        
    def test_dimension_target_positions(self):
        """Tests that when target positions are evaluated through evaluate_target_position,
        the dimension of the targets array is correct."""
        scanedges = self.scan_pars["scan_edges"]
        stepsize = self.scan_pars["stepsize"]
        targets = evaluate_target_positions(scanedges,stepsize)
        N_targets = 301
        assert N_targets == len(targets)
        
    def test_values_target_positions(self):
        """Tests that when target positions are evaluated through evaluate_target_position,
        the first and the last point of the target array is corrected"""
        scanedges = self.scan_pars["scan_edges"]
        stepsize = self.scan_pars["stepsize"]
        targets = evaluate_target_positions(scanedges,stepsize)
        assert isclose(scanedges[0],targets[0],rel_tol = 1e-8)
        assert isclose(scanedges[1],targets[-1],rel_tol = 1e-8)  # by induction is right because of linspace

    def test_save_data_file(self):
        """Tests that when processed data are saved through save_data_file,
        an output file named "cleaned_1D_data.txt" with the correct values is stored in the output folder.
        """
        # create fictitious targets 
        targets  = np.array([1,2,3,4,5],dtype=float)
        # create fictitious signal values
        avg_val = np.random.random(size = len(targets))
        # save file to "cleaned_1D_data.txt"
        save_data_file(targets,avg_val)
        # expected output
        expected_output = ''
        for i in range(len(targets)):
            expected_output += '\b'+str(targets[i])+', '+'{:.6f}'.format(avg_val[i])+'\n'
        # Read the file contents and compare with expected output
        with open("output/cleaned_1D_data.txt", "rb") as f:
            assert f.read(),expected_output
            
        
class TestInputValidator:
    """ A class to test that when invalid input scan parameters are inserted, an exeption is raised and the code stops the execution. 
     Although a lower-level control is already present in the internal PI subroutines, it takes time to be activated. 
     Therefore, this additional entrance control find out invalid inputs without the need of connecting to the PI instrument. 
    """
    def test_invalid_type(self):
        """Tests that when an invalid value of 'type' is passed to the validate_type function,
        an exception (ValueError) is raised."""
        type = "invalid"
        with pytest.raises(ValueError):
            validate_type(type)

    def test_invalid_scan_edges(self):
        """ Tests that when an invalid value of 'scan_edges' is passed to the validate_scan_edges function,
        an exception (ValueError) is raised """
        scan_edges = [-10, 110]
        with pytest.raises(ValueError):
            validate_scan_edges(scan_edges)
    
    def test_invalid_stepsize(self):
        """ Tests that an invalid value of 'stepsize' is passed to the validate_stepsize function,
        an exception (ValueError) is raised """
        stepsize = 200
        with pytest.raises(ValueError):
            validate_stepsize(stepsize)

    def test_invalid_velocity(self):
        """ Tests that when an invalid value of 'velocity' is passed to the validate_velocity function, 
        an exception (valueError) is raised """
        velocity = -5
        with pytest.raises(ValueError):
            validate_velocity(velocity)

    def test_invalid_acceleration(self):
        """ Tests that when an invalid value of 'acceleration' is passed to the validate_velocity function,
        an exception (ValueError) is raised """
        acceleration = 30
        with pytest.raises(ValueError):
            validate_acceleration(acceleration)

def test_valid_input(self):
        """Tests that when corrected values of scan parameters are provided, all the input validations 
        are successfull."""
        scanPars = {		
                "type": "discrete",
                "scan_edges": [0,1],
                "stepsize" : 0.1,
                "velocity" : 1,
                "acceleration" : 1,
                "sampling_freq" : 100
                }
        assert validate(scanPars)