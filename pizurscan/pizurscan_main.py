from InputValidator import input_validator
from Scanner import LineScan, PlaneScan
from PI_commands import Stepper, StepperChain
from InputProcessor import evaluate_daq_pars, evaluate_2D_daq_pars
from OutputProcessor import save_processed_data, save_processed_2D_data
import json
import sys
import keyboard
from colorama import Fore, Back, Style, init

def press_enter_to_continue():
    # """
    # Pauses the program execution until the user presses ENTER.
    # If the ESC key is pressed, the program terminates.
    # """
    print(Back.RED + "Program is pausing: when you're done working on the Zurich lock-in, press ENTER to continue, or ESC to exit.")
    print("Waiting for user input...")
    while True:
        pressed_key = keyboard.read_event()
        try:
            if pressed_key.name == 'esc':
                print("\nYou pressed ESC, so exiting...")
                print(Style.RESET_ALL)
                sys.exit(0)
            elif pressed_key.event_type == keyboard.KEY_DOWN and pressed_key.name == 'enter':
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
daq_pars = evaluate_2D_daq_pars(scan_pars)
print(Fore.GREEN +  "Here're the parameters that you should insert into the DAQ panel of the Zurich:")
for k, v in daq_pars.items():
    print(Back.WHITE + Fore.BLUE+k+": ", v)
print(Style.RESET_ALL)

press_enter_to_continue()

# instantiate the Scanner object
with PlaneScan(inpars) as scanner:
    try:
        if scan_pars["type"] == "continuous":
            scanner.execute_continuous_2D_scan()
        else:
            scanner.execute_discrete_2D_scan()
    except KeyboardInterrupt:
        StepperChain.close_daisy_chain_connection()
        print("Scan execution interrupted: closing program ...")

press_enter_to_continue()

# process data that are outputted by Zurich-lock in and saved into the output folder
save_processed_2D_data(filename = "dev4910_demods_0_sample_r_avg_00000.csv",
                        scan_pars = scan_pars,
                        daq_pars = daq_pars)

print("Scan data are saved to 'output/'. Closing the program ...")
