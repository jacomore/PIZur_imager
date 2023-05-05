# pizurscan
**pizurscan** is a library designed for interfacing two instruments: a [Stepper Motor Controller](https://www.physikinstrumente.com/en/products/controllers-and-drivers/motion-controllers-drivers-for-linear-torque-stepper-dc-servo-motors/c-66312-mercury-step-stepper-motor-controller-900553) by Physik Instrumente (PI) and the [Zhinst Lock-in](https://www.zhinst.com/europe/it/products/mfli-lock-in-amplifier). 
In particular, **pizurscan** calculates the parameters to be provided to the Zurich lock-in, controls the motion of the moving stage issued on the PI axis and associates data outputted by Zurich lock-in to the spatial positions of the stage.
**pizurscan** was developed by Giacomo rizzi ([Contact Me](mailto:rizzigiacomo@pm.me)) for controlling a newly developed experimental apparatus (based on these two instruments) for the University of Bologna ([DIFA](https://fisica-astronomia.unibo.it/it/index.html)). [Online documentation](https://pizur-imager.readthedocs.io/en/latest/) is available.

There are plenty of applications for such a technology. Let's start with the most general experiment: a sample, a probe and a physical quantity to be measured, which we call *signal*. \
Suppose that your probe (which we assume to be local) can be somehow issued on the moving stage of the PI stepper motor. In that case, you could potentially investigate the spatial dependence of the probed signal. As it would not make sense to probe a *global* property with a *local* techinque, let's assume that the signal that arises from the interaction of probe and sample comes from a localized region. 
If this part is indeed very localized, the collected signal may also be quite "small". Therefore, it is reasonable to use an AC stimuli as a probe and collect an AC signal in output. In this way one can exploit the filtering capabilities of a lock-in amplifier. 
Eventually, Zurich lock-in is a well-known fully digital lock-in amplifier that comes with a built-in DAQ (data acquisition board) that is very powerful for imaging applications.

The aim of the library is not to replace the two proprietary softwares, but just to make the interfacement between the two smoother. In addition to that, as it is quite straightforward to control the PI instrument directly from the API PYPIthon, scanning functionalities were also implemented into the library, therefore so that the user is only required to use the LabOne (Zurich software).

## Structure of the program
pizurscan simplifies the interaction between the two instruments with the following three features:

1. Input Processing: input parameters defining the trajectory and the cinematics of the PI stage are processed to evaluate the parameters that must be provided to the data acquisition (DAQ) of the Zhinst Lock-in.

2. Scan execution: the axis is directly controlled by pizurscan through the API PIPython <https://pypi.org/project/PIPython/>_. In particular, the user perform continuous and discrete scans: in the first, the stage moves continuously from the starting point to the final position, while in the second, small micrometric steps are performed, resting in a fixed position for around 50 ms.

3. Output Processing: When the trigger signal of the PI controller triggers the acquisition, the external signal is measured by the lock-in, and the DAQ integrates data over the acquisition time. Depending on the DAQ parameters evaluated with Input Processing, data outputted by the DAQ are further processed (integrated) so that eventually, a single value of the external signal is associated with the position of the stage.

Accordingly, the code defines four main classes: InputProcessor, Stepper, Scanner, and OutputProcessor. Such an OOP structure makes the three features described above independent of each other, so that one could potentially use only one/two of them. For instance, if raw data were previously acquired, one can use only the first and the last class for processing output data. Indeed, the roles of InputProcessor and OutputProcessor are the same as described in point 1 and 3. Stepper is the lower-level interface: it makes use of the PIPython API and is directly interfaced with the PI controllers. Scanner instantiates Stepper and combines the inherited methods for easing the overall handling of the controller connection and scanning procedures. In this way, the user does not need any knowledge of the PIPython library.


## Installation 

In order to connect to the PI device, you need first of all to install (and I am afraid, to buy) GCS DLLs (dynamic link libraries) provided by PI. For that the installation setup CD is needed. Anyway, if you are interested in this library I presume that you already have a PI instrument (and thus the needed libraries). Additionally, the following modules are necessary:

PIPython: an open-source library for accessing PI controllers through Python.
numpy: a fairly standard Python module used to handle numpy.arrays objects.
setuptools: a tool used for setting up the library.
Python 3.6 or later is required.

There are several ways to install the module:

1. The simplest way is to run either of these commands: pip install pizurscan or pip install --upgrade pizurscan. If you need to install pip, download getpip.py and run it with python getpip.py.
2. If you download the source of the module, then you can type: python setup.py install.
3. From Github, you can get the latest version and then type python setup.py install.
4. If you are completely lost, copying the folder pizurscan (the one that includes "init.py") from the source file into the same directory as your own script will work.

## Documentation and examples 
Extended documentation and examples can be found in the [Online documentation](https://pizur-imager.readthedocs.io/en/latest/)