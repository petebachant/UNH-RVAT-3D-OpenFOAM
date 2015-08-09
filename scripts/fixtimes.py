#!/usr/bin/env python
"""
This script looks through the time directories for empty files and creates
time files if necessary.
"""

from __future__ import division, print_function
import os


def is_time_dir(d):
    """Detect if a directory name is a non-zero time directory."""
    try:
        float(d)
    except ValueError:
        return False
    return d != "0"

def get_dirs():
    """Gets all local subdirectories."""
    return [name for name in os.listdir("./") if os.path.isdir(name)]
    
def is_empty(fname):
    """Tests if a file is empty or doesn't existy."""
    try:
        size = os.stat(fname).st_size
    except FileNotFoundError:
        return True
    return size == 0
    
    
text = r"""/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  2.3.x                                 |
|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      binary;
    class       dictionary;
    location    "{value}/uniform";
    object      time;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

value           {value};

name            "{value}";

index           {index};

deltaT          {dt};

deltaT0         {dt};


// ************************************************************************* //
"""

if __name__ == "__main__":
    dirs = get_dirs()
    dirs = [d for d in dirs if is_time_dir(d)]
    for d in dirs:
        fname = os.path.join(d, "uniform", "time")
        if is_empty(fname):
            print("Fixing {}".format(fname))
            with open(fname, "w") as f:
                i = int(float(d)/0.002)
                f.write(text.format(value=d, dt=0.002, index=i))
    print("End")
