.. _Doc&Ex:

Documents & Examples
======================
In :ref:`Getting started <getstarteddeep>` the general idea behind the structure of the code is provided. In this section three different examples are presented, which follows an order of complexity. 

Example 1: Scan execution
---------------------------
| Let's suppose that we only need to perform a line scan, without setting up the DAQ of the Zurich lock-in and processing output data. In case, the role of the user is to: 

#. Compile the :ref:`input_dicts <jsonfile>` with the appropriate parameters
#. Create a script file in the package folder ("pziruscan/pziruscan") with the :ref:`Code 1 <ex1>`. Please, note that if *"discrete"* scan is desired,  

.. _ex1:
.. code-block:: python
   :lineno-start: 1

    from pizurscan.Scanner import Scanner
    import json 

    # open and read scan parameters
    openPars = open('../input/input_dicts.json')
    inpars = json.load(openPars)
    scan_pars = inpars["scan_pars"]

    # instantiate the Scanner object
    scanner = Scanner() 
    scanner.connect_stepper()    # connect to PI device
    scanner.setup_motion_stepper()   # write velocity and acceleration in ROM
    try:
        if scan_pars["type"] == "continuous":
            scanner.init_stepper_scan()  # reference axis and move to first target position
            scanner.continuous_discrete_scan()  # perform continuous one dimensional scan
            break
        elif scan_pars["type"] == "discrete":
            scanner.init_stepper_scan()  # reference axis and move to first target position
            scanner.continuous_discrete_scan()  # perform discrete one dimensional scan
            break
        except: 
            scanner.stepper.close_connection()
            print("Be careful! scan 'type' must be either 'discrete' or 'continuous'...")
