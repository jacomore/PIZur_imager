.. _Doc&Ex:

Documents & Examples
======================
| In :ref:`Getting started <getstarteddeep>` the general idea behind the structure of the code is provided. In this section three examples are provided, for three different scenarios.

#. :ref:`Example 1 <ex1>`: can be applied when it is not required to interface the PI instrument with the Zurich lock-in, i.e, only a single line scan is needed. In this case the only two necessary modules are ``InputValidator`` and ``Scanner``. 
#. :ref:`Example 2 <ex2>`: can be applied when it is not required to execute the line scan (data were previously acquired), i.e, only post processing of the data is needed. In this case the three necessary modules are ``InputValidator``, ``InputProcessor`` and ``Outputprocessor``.
#. :ref:`Example 3 <ex3>`: can be applied in the most general scenario, i.e, the data need both to be acquired with the Zurich lock-in (and thus a scan must be executed) and post processed. In this case all the modules must be used.

Example 1: Scan execution
---------------------------
| Let's suppose that we only need to perform a line scan, without the need for setting up the DAQ of the Zurich lock-in and processing output data. In case, the role of the user is to: 

#. Compile the :ref:`input_dicts <jsonfile>` with the appropriate scan parameters
#. Create a script file in the package folder ("pizurscan/pizurscan") with the :ref:`Code 1 <ex1>`. 

.. _ex1:
.. code-block:: python
   :lineno-start: 1

    from Scanner import Scanner
    from pizurscan.InputValidator import InputValidator
    import json 
    import sys

    # open and read scan parameters
    openPars = open('../input/input_dicts.json')
    inpars = json.load(openPars)
    scan_pars = inpars["scan_pars"]

    # validate input data
    inputvalidator = InputValidator(scan_pars)
    try:
        inputvalidator.validate()
    except ValueError:
        print("Closing program ...")
        sys.exit()

    # instantiate the Scanner object
    scanner = Scanner(inpars) 
    scanner.connect_stepper()    # connect to PI device
    scanner.setup_motion_stepper()   # write velocity and acceleration in ROM
    scanner.init_stepper_scan()
    try: 
        if scan_pars["type"] == "continuous":
            scanner.execute_continuous_scan()
        else:
            scanner.execute_discrete_scan()
    except KeyboardInterrupt:
        scanner.stepper.close_connection()
        print("Scan execution interrupted: closing program ...")


Example 2: Data processing
---------------------------
| Let's suppose that we only need to process data acquired by the DAQ of the Zurich lock-in and processing output data. In case, the role of the user is to: 

#. Compile the :ref:`input_dicts <jsonfile>` with the appropriate scan parameters. Indeed, even though the scan will not be executed, the scan parameters
are still necessary for the InputProcessor class.  
#. Create a script file in the package folder ("pziruscan/pziruscan") with the :ref:`Code 2 <ex2>`. 

.. _ex2:
.. code-block:: python
   :lineno-start: 1

    from Scanner import Scanner
    from InputValidator import InputValidator
    import json 
    import sys

    # open and read scan parameters
    openPars = open('../input/input_dicts.json')
    inpars = json.load(openPars)
    scan_pars = inpars["scan_pars"]

    # validate input data
    inputvalidator = InputValidator(scan_pars)
    try:
        inputvalidator.validate()
    except ValueError:
        print("Closing program ...")
        sys.exit()

    # instance the input processor for evaluating daq parameters
    ip = InputProcessor(scan_pars)
    daq_pars = ip.evaluate_daq_pars()
    print("Data Acquisition parameters:")
    for k, v in daq_pars.items():
        print(k+": ", v)

    # instance output processor and save output data
    op = OutputProcessor(filename = "dev4910_demods_0_sample_r_avg_00000.csv",
                         scan_pars = scan_pars,
                         daq_pars = daq_pars)

    op.save_processed_data()




Example 3: Scan execution and data processing
----------------------------------------------
#. Compile the :ref:`input_dicts <jsonfile>` with the appropriate scan parameters
#. Create a script file in the package folder ("pizurscan/pizurscan") with the :ref:`Code 3 <ex3>`. 

.. _ex3:
.. code-block:: python
   :lineno-start: 1

    from Scanner import Scanner
    from InputValidator import InputValidator
    import json 
    import sys

    def press_any_key_to_continue():
    print("Press any key to continue, or ESC to exit.")
    while True:
        key = keyboard.read_event()
        try:
            if key.name == 'esc':
                print("\nyou pressed Esc, so exiting...")
                sys.exit(0)
            else:
                print("Continuing program...")
                break
        except:
            break

    # open and read scan parameters
    openPars = open('../input/input_dicts.json')
    inpars = json.load(openPars)
    scan_pars = inpars["scan_pars"]

    # validate input data
    inputvalidator = InputValidator(scan_pars)
    try:
        inputvalidator.validate()
    except ValueError:
        print("Closing program ...")
        sys.exit()

    # instance the input processor for evaluating daq parameters
    ip = InputProcessor(scan_pars)
    daq_pars = ip.evaluate_daq_pars()
    print("Data Acquisition parameters:")
    for k, v in daq_pars.items():
        print(k+": ", v)
    
    # wait time for writing parameters in the DAQ of the lock-in
    print("Please, now type the daq parameters into the DAQ of the Zurich lock ...")
    press_any_key_to_continue()

    # instantiate the Scanner object
    scanner = Scanner(inpars) 
    scanner.connect_stepper()    # connect to PI device
    scanner.setup_motion_stepper()   # write velocity and acceleration in ROM
    scanner.init_stepper_scan()
    try: 
        if scan_pars["type"] == "continuous":
            scanner.execute_continuous_scan()
        else:
            scanner.execute_discrete_scan()
    except KeyboardInterrupt:
        scanner.stepper.close_connection()
        print("Scan execution interrupted: closing program ...")


    print("Please, now move the file outputted by the Zurich DAQ into the 'output' folder ...")
    press_any_key_to_continue()

    # instance output processor and save output data
    op = OutputProcessor(filename = "dev4910_demods_0_sample_r_avg_00000.csv",
                         scan_pars = scan_pars,
                         daq_pars = daq_pars)

    op.save_processed_data()
    print("Scan data are saved to 'output/cleaned_1D_data.txt'. Closing the program ...")