#!/bin/sh

#SBATCH --time=24:00:00     # WALLTIME
#SBATCH -N1 	            # Number of nodes
#SBATCH --job-name UNH-RVAT-OpenFOAM
#SBATCH --account=FY140434  # WC ID 
#SBATCH -p ec               # Queue name

source activate py27

mpiexec -npernode 1 ./upload.py 
