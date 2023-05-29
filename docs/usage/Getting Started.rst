.. _getstarted:

Getting Started
===============

Installing and upgrading
---------------------------
| To install pizurscan DLLs (dynamic link libraries) provided by PI in the installation setup are needed. I presume that if you are interested in this library you also have a PI instrument (and thus the needed libraries). In addition to that, the following modules are necessary: 

* *PIPython*: open-source library for accessing PI controllers through Python.
* *numpy*: a fairly standard Python module to handle numpy.arrays objects.
* *setuptools*: tool used for setting up the library.

| Python 3.6 or later is required. 

| There are several ways to install the module:
#. Simplest: ``pip install pizurscan`` or ``pip install --upgrade pizurscan``. If you need to install pip, download getpip.py and run it with python getpip.py.
#. If you download the `source <https://pypi.org/project/pizurscan/#files>`_ of the module, then you can type: ``python setup.py install``.
#. From `Github <https://github.com/jacomore/PIZur_imager.git>`_, you can get the latest version and then type ``python setup.py install``.
#. If you are completely lost, copying the folder pizurscan (the one that includes "__init__.py") from the source file into the same directory as your own script will work.


.. _getstarteddeep:
Getting Started
-----------------

In the most general case, one would like to exploit all of the three features of pziruscan, namely input processing, scanning execution and output processing. To do so, the packages are imported as follows: 

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

The ``keyboard`` is optional and is used for pausing the program while writing the parameters in the DAQ pars.  
The `json <https://docs.python.org/3/library/json.html>`_ file "*input_dicts.json*" comprises two dictionaries; **scan_pars** and **pi**, which define respectively the parameters of the scan, such as the edges or the cinematic, and the parameters associated with PI instrument. 

.. _jsonfile:
.. code-block:: json
    :caption: input_dicts.json file

    {	
    "scan_pars" :
		{			
	"type": "continous",
        "scan_edges": [0,1],
        "stepsize" : 0.001,
        "velocity" : 1,
        "acceleration" : 2,
        "sampling_freq" : 1e3
		},
	"pi" : 
		{	
        "ID":"C-663",
        "stage_ID": "L-406.40SD00",
        "refmode": "FNL",
        "trig_type" : 6
		}
    } 
    
In particular, here a more detailed explanation of the parameter is provided:

#. **"scan_pars"**:

    * *type* : ``str`` object, can be either "*continuous*" or "*discrete*". In the first case, the PI stage moves continuously from the first target position (scan_edges[0]) up to the last one (scan_edges[1]). In the case of *discrete*, the scanning range is covered with a discretized trajectory, in which each target point is distant from the next of the quantity *stepsize*
    * *scan_edges*: ``list`` object, defines the edges of the scanning range in **[mm]**. The edges themselves are included in the target positions. Note that these two values must be comprised in the range [0,102].
    * *stepsize*: ``float`` object defining the stepsize (in  **[mm]**) of the target point partition. Note that it has a different meaning depending on the scan *type*. In case of a discrete scan, it defines the step size of the evenly spaced target points. In case of a continuous scan, it defines the number of fictituous subintervals in which the DAQ of the lock-in must resample the acquired data. For instance, in this case, one would have that the DAQ resamples the acquired data in 1/0.0001 + 1 = 1001 fictitiuous temporal subintervals that, by setting the correct duration of the acquisition, are analoguous to spatial subintervals of 1 micron each. 
    * *velocity*: ``float`` object defining the velocity (in [:math:`\frac{mm}{s}`]) of the PI stage during motion. Note that PI controller electronics allows for three feedback loops; on position, velocity and acceleration. Therefore this value is fixed with relatively high precision. 
    * *acceleration*: ``float`` object defining the acceleration (in [:math:`\frac{mm}{s^2}`]) of the PI stage during motion. Note that PI controller electronics allows for three feedback loops; on position, velocity and acceleration. Therefore this value is fixed with relatively high precision. 
    * *sampling_freq*: ``float`` object defining the sampling frequency of the Zurich lock-in for the external signal. This value is necessary to evaluate the duration of the acquisition time in case of discrete scan. 

#. **"pi"**:

    * *ID*: ``str`` object defining the serial number of the PI controller.
    * *stage_ID*: ``str`` object defining the serial number of the used PI axis (and thus the stage). 
    * *refmode*:  ``str`` object defining the edge reference of the PI stage is performed. It can be either *"FNL"* for refering at negative edge, i.e 0, or *"FPL"* for referencing at positive edge, i.e 102. 
    * *trig_type*:  ``int`` object defining the type of triggering to use. If set to 0, then a **line trigger** is produced by the PI controller every time the stage reaches a target position. However, the type of trigger upon which this software is developed is the 6. In this modality, every time the stage is motion, the trigger is **high**, whereas it goes **down** as soon as the stage stops. Therefore, when the *type* of scan_pars is not "continuous", the DAQ trigger on the positive edge (when the stage starts moving), while in "discrete" it triggers on the negative edge (when it stops in a position).

The import of *"input_dicts.json"* can be readily through the *input_validator* function, that not only transforms the entries of the "input_dicts.json" file into a Python dictionary, but also validates the compatibility/correctness of the input values. The import is performed as: 

.. code-block:: python

   :lineno-start: 1
    inpars = input_validator()
    scan_pars = inpars["scan_pars"]

Note that *scan_pars* can be easily selected because it is the value of the key *"scan_pars"* of inpars. 
| The function *evaluate_daq_pars* of the module InputProcessor processes the *scan_pars* extracted from the *inPars* dictionary and returns the parameters that should be input in the DAQ (data acquisition) tab of the Zurich lock-in. This is performed as follows:

.. code-block:: python
   :lineno-start: 1

    # process scan_pars to find the daq_pars
    daq_pars = evaluate_daq_pars(scan_pars)
    print(Fore.GREEN +  "Here're the parameters that you should insert into the DAQ panel of the Zurich:")
    for k, v in daq_pars.items():
        print(Back.WHITE + Fore.BLUE+k+": ", v)
    print(Style.RESET_ALL)

At that point, one may want to insert these parameters in the DAQ of the lock-in, which could take some time. A valid solution is to define a function for producing a pausing I/O interface: 

.. _pausefunc:
.. code-block:: python
   :lineno-start: 1

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


Now everything is ready for performing the desired scan. Let's suppose that one wants to perform a continuous scan with the parameters defined previously in file :ref:`input_pars <jsonfile>`. To connect the PI controller and perform the scan with the stage the following code can be used:

.. code-block:: python
   :lineno-start: 1

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

| If instead a discrete has to be executed the method *execute_continuous_scan* must be replaced with *execute_discrete_scan*. Easy, no?

| Last feature of pizurscan regards processing data outputted by the Zurich DAQ. With regards to that points, it must be noted that Zurich processes information through a Data server that runs on the instruments. For that reasons, data are not straightforward to extract in an automated matter. Therefore, **to process a certain output file, it is necessary to move/copy it into the folder *output*, where it is also saved the "cleaned" data file at the end of the output processing stage**. For this reason, in order for the data to be ready, it is necessary to call once again the function :ref:`press_any_key_to_continue <pausefunc>`. 

When the file is copied, the following statement can be execute: 


.. code-block:: python
   :lineno-start: 1

    save_processed_data(filename = "dev4910_demods_0_sample_r_avg_00000.csv",
                        scan_pars = scan_pars,
                        daq_pars = daq_pars)


and that's it, folks! The overall example can be found in :ref:`Documents & Examples <Doc&Ex>`