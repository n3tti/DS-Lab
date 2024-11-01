#!/bin/bash

#SBATCH --time=23:59:00
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1

#SBATCH --job-name=crawling
#SBATCH --output=slurm_log/%j.out

module load eth_proxy

# Go to the current folder
SCRIPTDIR=$(scontrol show job "$SLURM_JOB_ID" | awk -F= '/Command=/{print $2}')
SCRIPTDIR=$(realpath "$SCRIPTDIR")
cd $(dirname "$SCRIPTDIR")

source /users/$USER/miniconda3_x86/etc/profile.d/conda.sh
conda activate venv 

make start
