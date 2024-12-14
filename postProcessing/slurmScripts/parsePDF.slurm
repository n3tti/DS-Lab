#!/bin/bash
#SBATCH --job-name=parse_pdf           # Job name
#SBATCH --nodes=1                        # Total number of nodes
#SBATCH --ntasks=50                       # Total number of tasks
#SBATCH --cpus-per-task=1                # Number of CPUs per task
#SBATCH --time=00:10:00                  # Time limit (e.g., 1 hour)
#SBATCH --output=parse_pdf.out       # Output file
#SBATCH --error=parse_pdf.err         # Error file



srun --ntasks=50 --nodes=1 python -m ExtractPDFs.parsePDFs &

wait
