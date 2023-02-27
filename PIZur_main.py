from Scanner_classes import Scan_1D, Scan_2D
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np


if __name__ == '__main__':
    scanner = Scan_2D('input_dicts.json')
    scanner.execute_discrete_2D_scan()
