#!/usr/bin/env python
"""Generate the dynamic mesh dictionary with periodic `omega`

`omega` fluctuates with 3 periods per rotation, and a phase shift to put
the first peak at 80 degrees, to match experiments
"""

import foampy

U = 1.0
R = 0.5
meantsr = 1.9

foampy.gen_dynmeshdict(U, R, meantsr, cellzone="AMIsurface", npoints=400)
