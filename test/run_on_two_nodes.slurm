#!/bin/bash
#SBATCH --job-name=two_nodes_test   # Job name
#SBATCH --nodes=2                  # Request 2 nodes
#SBATCH --ntasks-per-node=1        # 1 task per node
#SBATCH --time=00:05:00            # Time limit (5 minutes)
#SBATCH --output=output_%j.log     # Standard output and error log

# Load necessary modules if required
# module load <module_name>

echo "Job is running on the following nodes:"
scontrol show hostname $SLURM_JOB_NODELIST

# Run the script on each node
srun ./dummy_script.sh
