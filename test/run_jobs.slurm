#!/bin/bash
#SBATCH --job-name=python_jobs           # Job name
#SBATCH --nodes=1                        # Total number of nodes (1 for manager + 3 for workers)
#SBATCH --ntasks=1                       # Total number of tasks (1 manager + 3 workers)
#SBATCH --cpus-per-task=1                # Number of CPUs per task
#SBATCH --time=01:00:00                  # Time limit (e.g., 1 hour)
#SBATCH --output=joutput.%j.out       # Output file
#SBATCH --error=jerror.%j.err         # Error file


source /users/eromanet/miniconda3_x86/envs/env/bin/python

# Run manager.py on one node
srun --ntasks=1 --nodes=1 python -m ExtractPDFs.manager &

# Run worker.py on three different nodes
#srun --ntasks=3 --nodes=3 python -m ExtractPDFs.worker &
wait
