#!/bin/sh
# Script for uploading data from the Sandia Red Mesa cluster. Should be called
# from the project root directory

#SBATCH --time=24:00:00     # WALLTIME
#SBATCH -N1 	            # Number of nodes
#SBATCH --job-name UNH-RVAT-OpenFOAM
#SBATCH --account=FY140434  # WC ID
#SBATCH -p ec               # Queue name

mpiexec -npernode 1 python scripts/upload-figshare.py
