#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  7 21:34:46 2013

@author: pete
"""
import sys
import foampy

if len(sys.argv) > 1:
    if sys.argv[1] == "-g":
        gui = True
else:
    gui = False

foampy.make_progress_bar(gui=gui)
