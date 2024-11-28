#!/bin/bash
#SBATCH --job-name=python_jobs           # Job name
#SBATCH --nodes=1                        # Total number of nodes (1 for manager + 3 for workers)
#SBATCH --ntasks=4                       # Total number of tasks (1 manager + 3 workers)
#SBATCH --cpus-per-task=1                # Number of CPUs per task
#SBATCH --time=01:00:00                  # Time limit (e.g., 1 hour)
#SBATCH --output=manager.out       # Output file
#SBATCH --error=manager.err         # Error file


source /users/eromanet/miniconda3_x86/etc/profile.d/conda.sh
conda activate env
WORKER_TASKS=$((SLURM_NTASKS - 1))
echo "Total tasks: $SLURM_NTASKS, Worker tasks: $WORKER_TASKS"

MANAGER_NODE=$(srun --ntasks=1 --nodes=1 hostname)

echo "Manager node is $MANAGER_NODE"  # Log the manager node for debugging

# Run manager.py on one node
srun --ntasks=1 --nodes=1 --nodelist=$MANAGER_NODE python -m ExtractPDFs.manager &

# Run worker.py on three different nodes
srun --ntasks=$WORKER_TASKS python -m ExtractPDFs.worker --manager-host $MANAGER_NODE &
wait
