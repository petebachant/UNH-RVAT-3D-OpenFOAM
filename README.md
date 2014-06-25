UNH-RVAT 3-D OpenFOAM case files
================================

Meshing procedure
-----------------

### `cfMesh`
Run surfaceFeatureEdges [inputfile] [outputfile] to extract edges and patches from input file

#### Patches from raw STL
all_0    |    lower shaft
all_1    |    upper shaft
all_2    |    strut 1
all_3    |    blade 1
all_4    |    strut 2
all_5    |    blade 2
all_6    |    blade 3
all_7    |    hub bottom
all_8    |    hub top
all_9    |    blade 3 top
all_10   |    blade 3 bottom
all_11   |    strut 3
all_12   |    blade 2 top
all_13   |    blade 2 bottom
all_14   |    blade 1 top
all_15   |    blade 1 bottom
all_16--21   |    hub sides
all_22   |    shaft top
all_23   |    shaft bottom
all_24   |    inlet
all_25   |    right wall
all_26   |    top
all_27   |    left wall
all_28   |    bottom
all_29   |    outlet

mesh1
-----
Stats using 2.3.0:

  * 5300 s to mesh.
  * High Re near walls. y+ ~ 36. 
  * Solves at about 12 h/s on 4 processes with maxCo = 8.0. 

mesh4
-----
Stats using 2.3.0:

  * 2754 s to mesh on 6 processes
  * Solves at around 8 hr/s
  * y+ at blades 5.3 average at last time step
  * 0.31 C_P
  * 1.1 C_D
  * Large discrepancies between each blade's torque contribution

mesh5
-----
Using 2.3.x

  * 0.31 C_P from 361 deg to 10 s
  * yPlus average is 3.5 at blades
  * 6 million cells
  * Strange patterns coming from top BC
  * Layers were most likely bad around trailing edge

mesh6
-----
Using 2.3.x-e461dd8f9394

  * yPlus average 3.8 at blades at 6 s
  * 5.6M cells
  * 0.33 C_P from 3361 deg to 6 s
  * Solved at 14 h/s


License
-------
Copyright (c) 2014 Peter Bachant

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/">
<img alt="Creative Commons License" style="border-width:0" src="http://i.creativecommons.org/l/by/4.0/88x31.png" />
</a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/"/>
Creative Commons Attribution 4.0 International License</a>.
