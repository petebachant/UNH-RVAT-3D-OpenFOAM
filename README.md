UNH-RVAT 3-D OpenFOAM case files
================================

[![DOI](https://zenodo.org/badge/doi/10.5281/zenodo.47927.svg)](http://dx.doi.org/10.5281/zenodo.47927)

These case files simulate the UNH-RVAT in three dimensions using OpenFOAM's
`pimpleDyMFoam` solver. Note this is somewhat of a personal scratchpad for
figuring out the settings, so this case may not run as-is on all
systems.


## Usage

  * All commands should be run from the top-level directory.
  * The mesh is generated with `scripts/Allrun.pre`.
  * The simulation is run with `scripts/Allrun.postmesh`.
  * Turbine performance can be displayed with `python scripts/perf.py`.
  * Post-processing is done with `scripts/Allrun.post`.


## Dependencies

### Running

  * OpenFOAM 2.3.x
  * foamPy (available via `pip install foampy`)


### Post-processing

  * swak4Foam
  * [OpenFOAM 2.3.x with modified `execFlowFunctionObjects`](https://github.com/petebachant/OpenFOAM-2.3.x/tree/functionObjMeshMotion)
  * NumPy
  * matplotlib
  * pandas


## License

Code is MIT licensed. See `LICENSE` for details.

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/">
<img alt="Creative Commons License" style="border-width:0" src="http://i.creativecommons.org/l/by/4.0/88x31.png" />
</a><br />All other materials licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/"/>
Creative Commons Attribution 4.0 International License</a>.
