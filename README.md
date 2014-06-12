UNH-RVAT 3-D OpenFOAM case files
================================

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

License
-------
Copyright (c) 2014 Peter Bachant

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/">
<img alt="Creative Commons License" style="border-width:0" src="http://i.creativecommons.org/l/by/4.0/88x31.png" />
</a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/"/>
Creative Commons Attribution 4.0 International License</a>.
