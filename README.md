UNH-RVAT 3-D OpenFOAM case files
================================

These case files simulate the UNH-RVAT in three dimensions using OpenFOAM's
`pimpleDyMFoam` solver. Note this is somewhat of my personal scratchpad for 
figuring out the settings, so this case may not run out of the box on all 
systems.

## Tags for various meshes

### `mesh1`
Stats using 2.3.0:

  * 5300 s to mesh.
  * High Re near walls. y+ ~ 36. 
  * Solves at about 12 h/s on 4 processes with maxCo = 8.0. 

### `mesh2`
Stats using 2.3.0:

  * 2754 s to mesh on 6 processes
  * Solves at around 8 hr/s
  * y+ at blades 5.3 average at last time step
  * 0.31 C_P
  * 1.1 C_D
  * Large discrepancies between each blade's torque contribution

### `mesh5`
Using 2.3.x

  * 0.31 C_P from 361 deg to 10 s
  * yPlus average is 3.5 at blades
  * 6 million cells
  * Strange patterns coming from top BC
  * Layers were most likely bad around trailing edge

### `mesh6`
Using 2.3.x-e461dd8f9394

  * yPlus average 3.8 at blades at 6 s
  * 5.6M cells
  * 0.33 C_P from 361 deg to 6 s
  * Solved at 14 h/s

### `mesh7`
Using 2.3.x-e461dd8f9394

  * yPlus average 2.6 at blades at 6 s
  * 9.2M cells
  * 0.35 C_P from 361 deg to 6 s
  * maxCo = 100, C_P went to 0.32 for maxCo = 80--60
  * Solved at 28 h/s on 6 processors
  * Meshed in 4000 s

### `mesh8`
Using 2.3.x-80038b51334b

  * yPlus 3.0 at blades at 5.95 s.
  * 8.4M cells (symmetryPlane).
  * 0.31 C_P from 360 degrees to 6 s.
  * maxCo = 100, varied throughout run, though. 
  * Solved at 60 h/s.
  * Meshed in about an hour.
  * Lots of torque variation between blades.
  * Vorticity shedding from shaft looks like the timestep is too large.

### `mesh9`

  * Made to run on RedMesa
  * Solves at about 5 h/s on 32 processes and maxCo = 30.

## License

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/">
<img alt="Creative Commons License" style="border-width:0" src="http://i.creativecommons.org/l/by/4.0/88x31.png" />
</a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/"/>
Creative Commons Attribution 4.0 International License</a>.
