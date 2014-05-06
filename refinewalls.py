#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script refines wall layers in OpenFOAM meshes. A single thick layer should be generated
with `snappyHexMesh`.
"""
import subprocess
import numpy as np

# Input parameters
nlayers = 16
expansion_ratio = 1.25
patches = ["shaft", "blades"]

# Compute all cell heights starting at the wall
c = [1]
for n in range(nlayers - 1):
    c.append(expansion_ratio*c[n])
c = np.asarray(c)

# Normalize cell heights so sum = 1
c = c/c.sum()

# Compute splitting ratios between all cells
s = [np.sum(c[0:-1])]
for n in range(1, nlayers-1):
    s.append(np.sum(c[0:-n-1])/np.sum(c[0:-n]))

# Run OpenFOAM utility to split wall layers
for patch in patches:
    for ratio in s:
        cm = "refineWallLayer -overwrite " + patch + " " + str(ratio)
        subprocess.call(cm, shell=True)
