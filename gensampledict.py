#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate sampleDict for multiple cross-stream profiles

by Pete Bachant (petebachant@gmail.com)

"""
from __future__ import division, print_function
import numpy as np
import os
import sys
import foampy

# Input parameters
setformat = "raw"
interpscheme = "cellPoint"
fields = ["U"]
x = 1.0
ymax = 1.83
ymin = -1.83
ny = 41
zmax = 1.21999
zmin = -1.21999
nz = 21

header = r"""/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  2.3.x                                 |
|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      sampleDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
"""

ypoints = np.array([-1.5, -1.375, -1.25, 1.0])
ypoints = np.append(ypoints, np.arange(-1, -0.799, 0.1))
ypoints = np.append(ypoints, np.arange(-.75, -0.001, 0.05))
ypoints = np.append(ypoints, 0.0)
ypoints = np.append(ypoints, -np.flipud(ypoints[:-1]))

setblock = """    profile_{z_H}
    {{ 
        type        cloud; 
        axis        y; 
        points      ({points}
                    );
    }}"""
    
def make_pointlist(x, ylist, z):
    pointlist=""
    point = "\n                        ({x} {y} {z})"
    for y in ylist:
        pointlist += point.format(x=x, y=y, z=z)
    return pointlist
    
def make_setblock(z_H):
    pointlist = make_pointlist(x, ypoints, z_H)
    return setblock.format(z_H=z_H, points=pointlist)
    
def make_all_text():
    z_array = np.arange(-1.125, 1.126, 0.125)
    
    txt = header + "\n" 
    txt += "setFormat " + setformat + "; \n\n"
    txt += "interpolationScheme " + interpscheme + "; \n\n"
    txt += "sets \n( \n"
    
    for z in z_array:
        txt += make_setblock(z) + "\n\n"
        
    txt += ");\n\n"
    txt += "fields \n(\n"
    
    for field in fields:
        txt += "    " + field + "\n"
        
    txt += "); \n\n"
    txt += "// *********************************************************************** // \n"
    return txt
    
def test_output():
    print(make_all_text())

def main():
    txt = make_all_text()
    with open("system/sampleDict", "w") as f:
        f.write(txt)

if __name__ == "__main__":
    main()
#    test_output()
