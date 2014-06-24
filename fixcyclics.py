#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script fixes the cyclic definitions in the boundary file

@author: pete
"""
header = r"""/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  2.3.0                                 |
|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/

"""

patches = ["AMI1", "AMI2"] # Must be in correct order in the file
tolerance = 0.0001
transform = "noOrdering"
neighbor_patches = ["AMI2", "AMI1"]

with open("constant/polyMesh/boundary", "r") as f:
    lines = f.readlines()
    lines_s = [line.strip() for line in lines]
    i0 = lines_s.index(patches[0])
    i1 = lines_s.index(patches[1])
    for n in range(i0, 100):
        if "}" in lines_s[n]:
            iend0 = n
            break
    for n in range(i1, 100):
        if "}" in lines_s[n]:
            iend1 = n
            break
    top = lines[:i0]
    patch0 = lines[i0:iend0]
    for subline in patch0:
        s = subline.split()
        if s[0] == "nFaces":
            nfacesline0 = subline
        elif s[0] == "startFace":
            sfaceline0 = subline
    patch0 = "    " + patches[0] + "\n    {\n        " + \
             "type cyclicAMI;\n        inGroups 1(cyclicAMI);\n" + \
             nfacesline0 + sfaceline0 + "        " + \
             "matchTolerance " + str(tolerance) + ";\n        " + \
             "transform " + transform + ";\n        " + \
             "neighbourPatch " + neighbor_patches[0] + ";\n"
    middle = lines[iend0:i1]
    patch1 = lines[i1:iend1]
    for subline in patch1:
        s = subline.split()
        if s[0] == "nFaces":
            nfacesline1 = subline
        elif s[0] == "startFace":
            sfaceline1 = subline
    patch1 = "    " + patches[1] + "\n    {\n        " + \
             "type cyclicAMI;\n        inGroups 1(cyclicAMI);\n" + \
             nfacesline1 + sfaceline1 + "        " + \
             "matchTolerance " + str(tolerance) + ";\n        " + \
             "transform " + transform + ";\n        " + \
             "neighbourPatch " + neighbor_patches[1] + ";\n"
    end = lines[iend1:]
    newtext = header + "".join(top) + patch0 + "".join(middle) + patch1 + "".join(end) + "\n"

with open("constant/polyMesh/boundary", "w") as f:
    f.write(newtext)
