#!/usr/bin/env python
"""Calculate turbine performance and print to the terminal."""

import sys
sys.path.append(".")
from pyurof3dsst.processing import calc_perf

calc_perf(plot=False, export_csv=True)
