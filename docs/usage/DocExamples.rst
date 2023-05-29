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
    from InputValidator import input_validator

    # extract and validate input data
    inpars = input_validator()
    scan_pars = inpars["scan_pars"]
    # instantiate the Scanner object
    with Scanner(inpars) as scanner:
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

    from InputValidator import input_validator
    from InputProcessor import evaluate_daq_pars
    from OutputProcessor import save_processed_data 

    # extract and validate input data
    inpars = input_validator()

    # process scan_pars to find the daq_pars
    daq_pars = evaluate_daq_pars(inpars["scan_pars"])

    # process data that are outputted by Zurich-lock in and saved into the output folder
    save_processed_data(filename = "dev4910_demods_0_sample_r_avg_00000.csv",
                        scan_pars = inpars["scan_pars"],
                        daq_pars = daq_pars)


Example 3: Scan execution and data processing
----------------------------------------------
#. Compile the :ref:`input_dicts <jsonfile>` with the appropriate input parameters
#. Create a script file in the package folder ("pizurscan/pizurscan") with the :ref:`Code 3 <ex3>`. 

.. _ex3:
.. code-block:: python
   :lineno-start: 1

    from InputValidator import input_validator
    from Scanner import Scanner
    from InputProcessor import evaluate_daq_pars
    from OutputProcessor import save_processed_data
    import json 
    import sys
    import keyboard
    from colorama import Fore, Back, Style, init

    def press_any_key_to_continue():
        """
        Pauses the program execution until the user presses any key.
        If the ESC key is pressed, the program terminates.
        """
        print(Back.RED +"Program is pausing: when you're done working on the Zurich lock-in, press any key to continue, or ESC to exit.")
        print("Waiting for user input...")
        while True:
            pressed_key = keyboard.read_event()
            try:
                if pressed_key.name == 'esc':
                    print("\nYou pressed ESC, so exiting...")
                    print(Style.RESET_ALL)
                    sys.exit(0)
                else:
                    print("Continuing program...")
                    print(Style.RESET_ALL)
                    break
            except:
                break

    init()
    # extract and validate input data
    inpars = input_validator()
    scan_pars = inpars["scan_pars"]
    # process scan_pars to find the daq_pars
    daq_pars = evaluate_daq_pars(scan_pars)
    print(Fore.GREEN +  "Here're the parameters that you should insert into the DAQ panel of the Zurich:")
    for k, v in daq_pars.items():
        print(Back.WHITE + Fore.BLUE+k+": ", v)
    print(Style.RESET_ALL)

    press_any_key_to_continue()

    # instantiate the Scanner object
    with Scanner(inpars) as scanner:
        try: 
            if scan_pars["type"] == "continuous":
                scanner.execute_continuous_scan()
            else:
                scanner.execute_discrete_scan()
        except KeyboardInterrupt:
            scanner.stepper.close_connection()
            print("Scan execution interrupted: closing program ...")

    press_any_key_to_continue()

    # process data that are outputted by Zurich-lock in and saved into the output folder
    save_processed_data(filename = "dev4910_demods_0_sample_r_avg_00000.csv",
                            scan_pars = scan_pars,
                            daq_pars = daq_pars)
                            
    print("Scan data are saved to 'output/cleaned_1D_data.txt'. Closing the program ...")